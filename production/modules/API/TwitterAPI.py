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
        ua = UtilAPI()
    
        #setup authorization
        auth = tw.OAuthHandler(ua.Param['twitter']['twitter_consumer_key'],ua.Param['twitter']['twitter_consumer_secret_key'] )
        auth.set_access_token(ua.Param['twitter']['twitter_access_token'],ua.Param['twitter']['twitter_access_token_secret'])

        #make API connection
        self.TA = tw.API(auth,wait_on_rate_limit=True)
        
        # END TwitterAPI