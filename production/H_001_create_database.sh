#!/bin/.sql

####################################################################
### Purpose: Set up database to host information for tweets  #######
### Author: Michael Turner                                   #######
### Date: 12/10/2020                                         #######
####################################################################

####
#### SET UP DATEBASE
####

#DROP DATABASE
DROP DATABASE haiku_db;

#CREATE DATABASE 
CREATE DATABASE haiku_db;

#USE DATABASE
USE haiku_db;

####
#### Create TREND TABLE
####

DROP TABLE IF EXISTS twitter_trend;

CREATE TABLE twitter_trend(

    #unique id for each future tweet
    trend_id INT NOT NULL AUTO_INCREMENT PRIMARY KEY
    
    #unique trend text that seed future tweets
    ,trend_text VARCHAR(240) NOT NULL
    
    #time this trend was uploaded into the database 
    ,load_dt DATETIME NOT NULL
);

####
#### END
####