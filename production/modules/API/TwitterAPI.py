# TwitterAPI FILE
# Author = Michael Turner
# Date = 11DEC2020
# Role = Hold Parameters and APIs for Twitter referenced across the entire platform

# twitter
import tweepy as tw

# util
from modules.API.UtilAPI import UtilAPI
        
class TwitterAPI:
    """Twitter API (TA)- Holds Based Twitter Keys and Setup Parameters"""
    
    def __init__(self):
        
        #initalize paramters
        Param = UtilAPI().Param
    
        #setup authorization
        auth = tw.OAuthHandler(Param['twitter']['twitter_consumer_key'],Param['twitter']['twitter_consumer_secret_key'] )
        auth.set_access_token(Param['twitter']['twitter_access_token'],Param['twitter']['twitter_access_token_secret'])

        #make API connection
        self.API = tw.API(auth,wait_on_rate_limit=True)
        
        # END TwitterAPI