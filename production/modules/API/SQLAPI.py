# SQLAPI FILE
# Author = Michael Turner
# Date = 11DEC2020
# Role = Hold Basic Parambetes for entering and dealing with the database 

# mysql
from mysql.connector import (connection)

# util
from modules.API.UtilAPI import UtilAPI
        
class SQLAPI:
    """SQL Database API (SA) - Holds Basic MySQL Connection"""
        
    def __init__(self):
        
        #initalize Param for inputs
        ua = UtilAPI()
        
        #connect to database 
        self.db = connection.MySQLConnection(host=ua.Param['system']['host'],user=ua.Param['system']['user'],password= ua.Param['sql']['password'])
        
        #connect cursor
        self.DbCursor = self.db.cursor(buffered=True)
        
        # END SQLAPI