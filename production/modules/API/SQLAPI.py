# SQLAPI FILE
# Author = Michael Turner
# Date = 11DEC2020
# Role = Hold Basic Parambetes for entering and dealing with the database 

#spark
from pyspark import SparkContext
from pyspark.sql import SparkSession, SQLContext

# mysql
from mysql.connector import (connection)

# util
from modules.API.UtilAPI import UtilAPI
        
class SQLAPI:
    """SQL Database API (SA) - Holds Basic MySQL Connection"""
        
    def __init__(self,SparkContext):
        
        #spark connection
        self.sc = SparkContext
        
        #initiate sql context (do not use directly, but enables toDF())
        sqlContext = SQLContext(self.sc)
        
        #initalize Param for inputs
        self.Param = UtilAPI().Param

        #connect to database 
        self.DB = connection.MySQLConnection(host=self.Param['system']['host'],user=self.Param['system']['user'],password= self.Param['sql']['password'])

        #connect cursor
        self.DBCursor = self.DB.cursor(buffered=True)
        
    def createTable(self,df,primaryKey):
        """ based on a pyspark table, creates a table of those same characteristics
        
        Args:
            df (pyspark.sql.dataframe.DataFrame) = data of the query
            primaryKey (list) = list of columns that compose the primary key
            
        Return
            string = string required to create a table for the Data Frame
            
        """
        
    def createTable(self,df,primaryKey,table,database=None):
            """ based on a pyspark table, creates a table of those same characteristics

            Args:
                df (pyspark.sql.dataframe.DataFrame) = data of the query
                primaryKey (list) = list of columns that compose the primary key
                table (string) = name of table information to be inserted into
                database (string) = name of database that contains the table that will be inserted into

            Return
                string = string required to create a table for the Data Frame

            """
            # set database as needed
            if database is None:
                database = self.Param['sql']['database_name'] 
                
            # get the columns an the data types
            dtype = df.dtypes
                
            # insure primary key - take first column if none are specified 
            if primaryKey is None:
                primaryKey = [dtype[0][0]]

            # create table
            createString = f'CREATE TABLE {database}.{table} ('
            
            # add in the each of the columns and keys
            for i,col in enumerate(dtype):
                typeHolder = (self.Param['sql']['type_conversion'][col[1]])
                createString += f'{col[0]} {typeHolder}'
                
                # for those columns that are in primary key
                if col[0] in primaryKey:
                    createString += " PRIMARY KEY"
               
                # complete increment
                createString +=", "
                
            # snip off last comma and replace with paranethese to end
            createString = createString[:-2]+" )"
                
            # create table
            self.DBCursor.execute(createString)

            # commit
            self.DB.commit()
            
            # end
        
    def dropTable(self,table,database=None):
        """ drop a specific table

            Args:
                table (string) = name of table information to be inserted into
                database (string) = name of database that contains the table that will be inserted into
        """
        # set database as needed
        if database is None:
            database = self.Param['sql']['database_name'] 
            
        # drop the table
        dropStr = f'''DROP TABLE IF EXISTS {database}.{table}'''
        self.DBCursor.execute(dropStr)

        # commit
        self.DB.commit()
        
        # end

    def query(self,query):
        """ queries database.
        
        Args:
            query (string) = query for mysql database.  Only for gathering information. Note, all queries are assumed to be in only lower case.
            
        Return
            pyspark.sql.dataframe.DataFrame = data of the query
            """
        #execute query
        self.DBCursor.execute(query.lower())

        #commit to send query to db
        self.DB.commit()

        #return spark dataframe
        return self.sc.parallelize(self.DBCursor.fetchall()).toDF([x[0] for x in self.DBCursor.description])
    
    #insert into database
    def insert(self,df,table,primaryKey=None,database=None,append=False):
        """ insert information into database
        
        Args:
            df (pyspark.sql.dataframe.DataFrame) = df to be uploaded 
            table (string) = name of table information to be inserted into
            primaryKey (list) = list of columns that compose the primary key
            database (string) = name of database that contains the table that will be inserted into
            append (boolean) = if True append rows, if False delete and recreate table with new data
            
        Returns
            NULL (no return)"""
        
        #set database as needed
        if database is None:
            database = self.Param['sql']['database_name'] 
        
        #if needed delete the existing table and replace
        if append == False:
            
            # drop table
            self.dropTable(table=table,database=database)
            
            #create table
            self.createTable(df=df,table=table,primaryKey=primaryKey,database=database)
            
           
        # insert into statement
        insertText = f"insert into {database}.{table} ("+ ", ".join(df.columns) + ") VALUES (" +", ".join(['%s' for x in df.columns]) + ")"
        
        # insert values
        self.DBCursor.executemany(insertText, df.collect())
        
        #commit
        self.DB.commit()
        
        # end