# @file insta.py
# @author Kristin Linn
# @date 10-6-15
# @brief Helper functions that interact with IG API
import random
import os
from instagram.client import InstagramAPI

CITIES_STR = os.environ['CITIES']
CITIES_STR = CITIES_STR[2:-2]
CITIES = [c for c in CITIES_STR.split('\", \"')]

ID = os.environ['CLIENT_ID']
SECRET = os.environ['CLIENT_SECRET']

CONFIG = {
    'client_id': ID,
    'client_secret': SECRET,
    'redirect_uri': 'http://pinpoint.elasticbeanstalk.com/oauth_callback'
}

unauthenticated_api = InstagramAPI(**CONFIG)

# api = InstagramAPI(client_id=ID, client_secret=SECRET)

# Return a randomly chosen city from those in the database
def getUrls(token):
    global CITIES
    global CONFIG
    n = len(CITIES)
    someError = True
    while someError:
        urls = []
        rCity = CITIES[random.randint(0, n-1)]
        try:
            api = InstagramAPI(access_token=token, client_secret=CONFIG['client_secret'])
            cityCall, next_ = api.tag_recent_media(count=32, tag_name=rCity+"skyline")
        except:
            print "API error on first call"
        else:
            someError = False
            for l in range(len(cityCall)):
                imgUrl = cityCall[l].get_standard_resolution_url()
                if imgUrl.split(".")[-1]!="jpg":
                    continue
                if imgUrl.find("s640x640")==-1:
                    continue
                urls.append(imgUrl)
    random.shuffle(urls)
    return rCity, urls





