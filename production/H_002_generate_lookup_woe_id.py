#!/usr/bin/env python
# coding: utf-8

# # Purpose 
# Understand mapping between Twitter IDs for cities, city names, and city populations (ie - how many users in those cities) <br>
# Generate Table 

# # 0.0 Imports 

#basic packages
import re
import os 
import sys
from collections import Counter

#data manipulation
import numpy as np
import pandas as pd

#import web and html packages
import requests
from bs4 import BeautifulSoup as bs

#spark 
from pyspark import SparkContext
from pyspark.sql import SparkSession, SQLContext, Row, Window
from pyspark.sql.types import StringType, IntegerType, FloatType, DoubleType
import pyspark.sql.functions as F

#get APIs 
#get modules
from modules.API.UtilAPI import UtilAPI
from modules.API.TwitterAPI import TwitterAPI
from modules.API.SQLAPI import SQLAPI

# ## 0.1 Setup Connections 

#params
Param = UtilAPI().Param

#setup spark connection
sc = SparkContext(Param['system']['spark_host'],appName="nb_city_twitter_match")

#initiate sql context (do not use directly, but enables toDF())
sqlContext = SQLContext(sc)

#setup twitter connectin
Twitter = TwitterAPI()

#setup database connection
DB = SQLAPI(SparkContext=sc)

# # 1.0 Gather Twitter Trends 

# Extract Trends From Twitter 
trendRaw = Twitter.API.trends_available()

# Parallelize 
trendParallel = sc.parallelize([[y for i,y in enumerate(x.values()) if i in [0,5,6]] for x in trendRaw]).toDF(['city_name','woe_id','country_code'])

# Clean
#transform function 
def cityClean(x):
    """basic cleaning of city names"""
    
    #lowercase
    x = x.lower()
    
    #remove periods
    x =  re.sub(r"\.","",x)
    
    #remove brackets - and the things within them
    x = re.sub(r'''\[.*\]''','',x)
    
    #for state, remove non ascii character for flag
    x = re.sub(r'''\xa0''','',x)
    
    #replace white space with underscores (strip)
    x = re.sub(r"\s+","_",x.strip())
    
    #return
    return x 

#make spark function
udfCityClean = F.udf(cityClean, StringType())

trend = (trendParallel

#from overall trend analysis only look at american cities 
.filter(F.col('country_code')=='US')\

#for city names replace spaces with underscores and all lower case to aid joins
#with column name apply function to data in name, then replace this new column with original with overriding alias
.withColumn("city_name",udfCityClean("city_name")))

#show head
trend.take(5)


# Make the names of some cities clearer for code to understand
#new york --> new york city
trend = trend.withColumn("city_name", F.when(F.col("city_name")=='new_york', 'new_york_city').otherwise(F.col("city_name")))

#'dallas-ft_worth' --> 'fort_worth'
trend = trend.withColumn("city_name", F.when(F.col("city_name")=='dallas-ft_worth', 'fort_worth').otherwise(F.col("city_name")))

# # 2.0 Gather City Information 

# Scrap Wikipeida 
page = requests.get('''https://en.wikipedia.org/wiki/List_of_United_States_cities_by_population''')

# Get soup
soup = bs(page.text, 'html.parser')

# Get Table 
wikiTable = soup.findAll('table')[4]

# Parse table - remove headers and get the text of the results 
wikiTableTight = [x for x in wikiTable.text.strip().split("\n") if len(x) != 0][9:]

# Extract the rows of interest in an organized manner 
# hold information about the cites
rowHolder = []

#increment ot proceed through the table (columns of interest in wikipedia table)
incr = 11

#index holder to increment through
startHolder = 0

#halt at 252 because a pair of cities have the same population and warp the table 
#we have the cities we are interested in
for i in range(0,252):
    
    #add new city to structured df
    rowHolder = rowHolder + [wikiTableTight[startHolder:startHolder+ incr]]
    
    #increment range
    startHolder += incr

# Parallelize Wikipeida table 
cityInfoRaw = sc.parallelize(rowHolder).toDF(['rank'
                                ,'city_name'
                                ,'state_name'
                                ,'population_2019'
                                ,'population_2010'
                                ,'population_change'
                                ,'land_sq_mile'
                                ,'land_sq_km'
                                ,'population_density_per_sq_mile'
                                ,'population_density_per_sq_km'
                                ,'latitude_longitude'])


# Clean Wikipedia table
# function to clean the columns of interest 
def stringFloat(x):
    """ returns cleaned integer, sans ,"""
    return float(re.sub(r',','',x))

#function to get longitude and latiude into two clean numeris columns
#indicate split in
def latiudeCleaner(x):
    """ takes string latitude and turns into numerics
    Args:
        x (string) = raw input string
        
    Returns:
        float = latitude of query 
    """
    #get latitude
    latitude=x.split(" ")[0]

    #indicators if north or south of the equator
    northSouth = 1
    if 'S' in latitude:
        northSouth = -1

    #turn latitude and longitude into numbers
    latitude = re.findall("\d+", latitude)
    
    #make float and return - zero to attempt to handle floating point errors
    return float(latitude[0]+"."+ ''.join(latitude[1:]))* northSouth
    
def longitudeCleaner(x):
    """ takes string longitude and turns into numerics
    Args:
        x (string) = raw input string
        
    Returns:
        float = longitude of query 
    """
    #get longitude
    longitude = x.split(" ")[1]

    #indicatores if east or west of prime meridan
    eastWest = 1
    if 'W' in longitude:
        eastWest = -1

    #get only digits
    longitude = re.findall("\d+", longitude)
    
    #make float 9zero to attempt to handle floating point errors
    return float(longitude[0]+"."+ ''.join(longitude[1:])) * eastWest
    
#make spark functions (uses double type for more precision)
udfStringFloat= F.udf(stringFloat, DoubleType())
udfLatiudeCleaner = F.udf(latiudeCleaner, DoubleType())
udfLongitudeCleaner= F.udf(longitudeCleaner, DoubleType())

# Conduct Basic Data Cleaning of Columns 
cityInfo = (cityInfoRaw
            
#for city names replace spaces with underscores and all lower case to aid joins
#with column name apply function to data in name, then replace this new column with original with overriding alias
.withColumn("city_name",udfCityClean("city_name"))\
            
#clean state names
.withColumn("state_name",udfCityClean("state_name"))\

#clean population counts for 2019
.withColumn('population_2019',udfStringFloat("population_2019"))\
            
#clean population counts for 2010
.withColumn('population_2010',udfStringFloat("population_2010"))\
            
#clean and return latitude (floats have wierd 
.withColumn('latitude',udfLatiudeCleaner("latitude_longitude"))\
        
#clean and return longitude
.withColumn('longitude',udfLongitudeCleaner("latitude_longitude"))\
            
#change rank to integer
.withColumn("rank", cityInfoRaw["rank"].cast(IntegerType()))\
            
#drop columns
.drop('population_change','land_sq_mile','land_sq_km','population_density_per_sq_mile','population_density_per_sq_km','latitude_longitude')
            
#end
)

# With data cleaned and organized, create new columns related to population change
#change the population change number to a more percise double
cityInfo = cityInfo.withColumn('population_change',cityInfo.population_2019/cityInfo.population_2010)

# Add in United States as well
usInfo = sc.parallelize([Row(rank=0
                   , city_name='united_states'
                   , state_name='united_states'
                   , population_2019=331923317.0
                   , population_2010=308745538.0
                   , latitude=40.1611
                   , longitude=-76.5232
                   , population_change=1.0750708144646937)]).toDF(cityInfo.columns)

# Union
cityInfo = usInfo.union(cityInfo)


# Add in Harrisburg as well ( Twitter has it, but not in list of top 252 cities)
harrisInfo = sc.parallelize([Row(rank=cityInfo.agg({'rank': 'max'}).take(1)[0]['max(rank)']+1
                   , city_name='harrisburg'
                   , state_name='pennsylvania'
                   , population_2019=48710.0
                   , population_2010=49528.0
                   , latitude=39.50 
                   , longitude=-98.35
                   , population_change=0.9834840898077855)]).toDF(cityInfo.columns)

# Union
cityInfo = cityInfo.union(harrisInfo)

# Remove Cities with redundant city name primary key (removing the smaller city without a twitter trend )
# drop kansas_city, kansas (missouri called dibs, though it is profoundly unfair)
cityInfo = cityInfo.filter(~((F.col('city_name')=='kansas_city') & (F.col('state_name')=='kansas')))
# drop columbus, georgia
cityInfo = cityInfo.filter(~((F.col('city_name')=='columbus') & (F.col('state_name')=='georgia')))


# # 3.0 Merge 
# Get population information taken together with the city information
trendUnion = trend.join(cityInfo,on="city_name",how="inner").sort(F.col("rank"))

# ## 3.1 Clean Up Column Names for better interpretabilty 

# Update the Rank Column - Most Common to Least Common <br>
# Get the new ranks and Revise the ranks 

# drop the original ranks 
trendUnion = trendUnion.drop('rank')

# create a column to rank on (inverse of population)
trendUnion = trendUnion.withColumn('neg_population_2019',F.col('population_2019')*-1)

# develop ranks
trendUnion = trendUnion.withColumn("rank",F.dense_rank().over(Window.orderBy("neg_population_2019")))

# drop rank column
trendUnion = trendUnion.drop('neg_population_2019')

# sort by trends
trendUnion = trendUnion.sort('rank')

# Add indicator if state or country 
trendUnion = trendUnion.withColumn("territory_type", F.when(F.col("city_name")=='united_states', 'country').otherwise('city'))


# Rename and organize columns
trendUnion = trendUnion.selectExpr(
    "woe_id"
    ,"city_name as target_name"
    ,"state_name as region_name"
    ,"country_code as country_name"
    ,"latitude"
    ,"longitude"
    ,"population_2019 as population"
    ,"population_2010"
    ,"rank"
    ,"territory_type")

# # 4.0 Input Table Into MySQL Database  
DB.insert(df=trendUnion,table='lookup_woe_id',primaryKey=['woe_id'],database=Param['sql']['database_name'],append=False )

# # End 