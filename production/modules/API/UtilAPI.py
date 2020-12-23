# UTIL FILE
# Author = Michael Turner
# Date = 11DEC2020
# Role = Hold Parameters and APIs referenced across the entire platform

# imports 
# system
import os
import collections

class UtilAPI:
    """Utility API (UA)- Holds Basic Inputs From Throughout Model"""
    def __init__(self):
        
        #parameters for input (dictionary of dictionaries)
        self.Param = collections.defaultdict(dict)
        
        #user information
        self.Param['system']['user'] = "pi"
        self.Param['system']['host'] = "localhost"
        self.Param['system']['spark_host'] = "local"
        
        #twitter information 
        self.Param['twitter']['twitter_consumer_key'] = os.environ['twitter_consumer_key']
        self.Param['twitter']['twitter_consumer_secret_key'] = os.environ['twitter_consumer_secret_key']
        self.Param['twitter']['twitter_access_token'] = os.environ['twitter_access_token']
        self.Param['twitter']['twitter_access_token_secret'] = os.environ['twitter_access_token_secret']
        
        #database information
        self.Param['sql']['database_name'] = 'haiku_db'
        self.Param['sql']['password'] = os.environ['mysql_password']
        
        #database type conversion (pyspark --> mysql)
        self.Param['sql']['type_conversion'] = {'int' : 'BIGINT',
                                                'bigint': 'BIGINT',
                                                'string':'VARCHAR(100)',
                                                'double': 'DOUBLE',
                                                'float': 'DOUBLE',
                                                'boolean':'BOOLEAN',}
        
        #END UtilAPI