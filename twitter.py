import requests
import json
import time
import os
import sys
import codecs

from requests_oauthlib import OAuth1

# authentication pieces
client_key    = "14RdwJwcED1RkanxC5QdLLgeF"
client_secret = "lY2NG8dk082YcG16TEWndihyn7Gmh7mCOmYsFaTlTUakkZ9cva"
token         = "2920967563-NE93uzMVjJaxrsYSdzpJAyFPTlCdRKLSo5in92A"
token_secret  = "CeM8uEWVa8J9Iq0esKaoNab51Vhy9KUSmj1QFXz6iaQ5G"

# the base for all Twitter calls
base_twitter_url = "https://api.twitter.com/1.1/"

# setup authentication
oauth = OAuth1(client_key,client_secret,token,token_secret)

username           = sys.argv[1]

desktop_directory  = "%s/Social/twitter/Exporter/" % os.path.expanduser("~")

try:
    os.mkdir("%s%s" % (desktop_directory,username))
except:
    pass

try:
    os.mkdir("%s%s/photos" % (desktop_directory,username))
except:
    pass

log = codecs.open("%s%s/twitter.csv" % (desktop_directory,username),"wb",encoding="utf-8")
log.write("#,Created Timestamp, Text, Longitude, Latitude\r\n")

#
# Main Twitter API function for sending requests
#
def get_usernames(user_ids):

    
    url = "https://api.twitter.com/1.1/users/lookup.json?user_id=%s" % (user_ids)
    
          
    response = requests.get(url,auth=oauth)
    
    time.sleep(3)
    
    if response.status_code == 200:
        
        result = json.loads(response.content)
        
        usernames = []
        
        for i in result:
            usernames.append("%s,%s" % (i['screen_name'],i['name']))
        
        return usernames
    
    return None

#
# Main Twitter API function for sending requests
#
def send_request(screen_name,relationship_type,next_cursor=None):

    
    url = "https://api.twitter.com/1.1/%s/ids.json?screen_name=%s&count=5000" % (relationship_type,username)
    
    if next_cursor is not None:
        url += "&cursor=%s" % next_cursor
        
    response = requests.get(url,auth=oauth)
    
    time.sleep(3)
    
    if response.status_code == 200:
        
        result = json.loads(response.content)
        
        return result
    
    return None


#
# Function that contains the logic for paging through results
#
def get_all_friends_followers(username,relationship_type):
    
    account_list = []
    next_cursor  = None
    
    # send off first request
    accounts = send_request(username,relationship_type)
    
    # valid user account so start pulling relationships
    if accounts is not None:
        
        account_list.extend(accounts['ids'])
        
        print "[*] Downloaded %d of type %s" % (len(account_list),relationship_type)

        
        # while we have a cursor keep downloading friends and followers
        while accounts['next_cursor'] != 0 and accounts['next_cursor'] != -1:

            accounts = send_request(username,relationship_type,accounts['next_cursor'])
            
            if accounts is not None:
                
                account_list.extend(accounts['ids'])
                print "[*] Downloaded %d of type %s" % (len(account_list),relationship_type)

            else:
                
                break
    
     
    return account_list



#
# Download Tweets from a user profile
#
def download_tweets(screen_name,number_of_tweets,max_id=None):
    
    api_url  = "%s/statuses/user_timeline.json?" % base_twitter_url
    api_url += "screen_name=%s&" % screen_name
    api_url += "count=%d" % number_of_tweets
    
    if max_id is not None:
        api_url += "&max_id=%d" % max_id

    # send request to Twitter
    response = requests.get(api_url,auth=oauth)
    
    if response.status_code == 200:
        
        tweets = json.loads(response.content)
        
        return tweets
    
    else:
        
        print "[*] Twitter API FAILED! %d" % response.status_code
    

    return None

#
# Takes a username and begins downloading all Tweets
#
def download_all_tweets(username):
    full_tweet_list = []
    max_id          = 0
    
    # grab the first 200 Tweets
    tweet_list   = download_tweets(username,200)
    
    # grab the oldest Tweet
    if tweet_list is None:
        return
    
    oldest_tweet = tweet_list[-1]
    
    # continue retrieving Tweets
    while max_id != oldest_tweet['id']:
    
        full_tweet_list.extend(tweet_list)

        # set max_id to latest max_id we retrieved
        max_id = oldest_tweet['id']         

        print "[*] Retrieved: %d Tweets (max_id: %d)" % (len(full_tweet_list),max_id)
    
        # sleep to handle rate limiting
        time.sleep(3)
        
        # send next request with max_id set
        tweet_list = download_tweets(username,200,max_id-1)
    
        # grab the oldest Tweet
        if len(tweet_list):
            oldest_tweet = tweet_list[-1]
        

    # add the last few Tweets
    full_tweet_list.extend(tweet_list)
        
    # return the full Tweet list
    return full_tweet_list 
    
    

full_tweet_list = download_all_tweets(username)

print "[*] Retrieved %d Tweets. Processing now..." % len(full_tweet_list)

count = 1

# loop over each Tweet and print the date and text
if full_tweet_list is not None:
    
    print "[*] Processing %d of %d" % (count,len(full_tweet_list))
    
    for tweet in full_tweet_list:
        
        
        text = tweet['text'].replace("\"","").replace(",","")
        
        if tweet.has_key("extended_entities"):
            if tweet['extended_entities'] is not None:
                if tweet['extended_entities'].has_key("media"):
                    
                    for media in tweet['extended_entities']['media']:
                        
                        print "[*] Downloading photo %s" % media['media_url']
                        
                        response = requests.get(media['media_url'])
    
                        file_name = media['media_url'].split("/")[-1]
                        
                        fd = open("%s%s/photos/%s" % (desktop_directory,username,file_name),"wb")
                        fd.write(response.content)
                        fd.close()
                    
        
        if tweet["coordinates"] is not None:
            latitude  = tweet["coordinates"]["coordinates"][0]
            longitude = tweet["coordinates"]["coordinates"][1] 
        else:
            if tweet["place"] is not None:
                latitude = tweet["place"]["full_name"].replace(",","")
                longitude= tweet["place"]["country"]
            else:    
                latitude  = "None"
                longitude = "None"
            
        
        
        message = "%s,%s,%s,%s,%s\r\n" % (tweet['id'],tweet['created_at'],text,latitude,longitude)
        log.write(message)
        log.flush()
        
    count += 1

print "[*] Done. Now retrieving friends and followers."

friends = get_all_friends_followers(username,"friends")
followers = get_all_friends_followers(username,"followers")


count         = 0
final_friends = []

print "[*] Converting User ID to Usernames..."

while count < len(friends):
    
    friends_snippet = []
    
    if count < (len(friends)-101):
        index = count + 100
    else:
        index = count + (len(friends) - count)
    
    for friend in friends[count:index]:
        friends_snippet.append(str(friend))
        
    
    final_friends.extend(get_usernames(",".join(friends_snippet)))
    
    
    count += 100
    
fd = codecs.open("%s%s/friends.csv" % (desktop_directory,username),"wb",encoding="utf-8")
fd.write("\r\n".join(final_friends))
fd.close()


final_followers = []
count           = 0
while count < len(followers):
    
    followers_snippet = []
    
    if count < (len(followers)-101):
        index = count + 100
    else:
        index = count + (len(followers) - count)
    
    for follower in followers[count:index]:
        followers_snippet.append(str(follower))
    
    final_followers.extend(get_usernames(",".join(followers_snippet)))
    
    count += 100

fd = codecs.open("%s%s/followers.csv" % (desktop_directory,username),"wb",encoding="utf-8")
fd.write("\r\n".join(final_followers))
fd.close()

print "[*] Done!"
