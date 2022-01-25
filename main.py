# For sending GET requests from the API
import requests
# For saving access tokens and for file management when creating and adding to the dataset
import os
# For dealing with json responses we receive from the API
import json
# For displaying the data after
import pandas as pd
# For saving the response data in CSV format
import csv
# For parsing the dates received from twitter in readable formats
import datetime
import dateutil.parser
import unicodedata
#To add wait time between requests
import time
#For manage environment
#Credit to Andrew Edward for guidelines

#Export bearer_token to set environment variables
bearer_token = os.environ.get("BEARER_TOKEN")

def auth():
    return os.getenv('TOKEN')

def create_headers(bearer_token):
    headers = {"Authorization": "Bearer {}".format(bearer_token)}
    return headers

def create_url(keyword, start_date, end_date, max_results = 10):
    #First using recent search url API to pull interested keyword
    # search_url = "https://api.twitter.com/2/tweets/search/recent"
    
    #Tweet search url
    # search_url = "https://api.twitter.com/2/tweets"
    
    #Retweet search url
    search_url = "https://api.twitter.com/2/tweets/"+keyword+"/retweeted_by"
    
    # #Querry params for recent search
    # query_params = {'ids': keyword,
    #                 # 'start_time': start_date,
    #                 # 'end_time': end_date,
    #                 # 'max_results': max_results,#Min 10, max 100
    #                 #Expansion: Expands payload of ID into complete object, stores in jason['includes']
    #                 'expansions': 'author_id,in_reply_to_user_id,geo.place_id',
    #                 'tweet.fields': 'id,text,author_id,in_reply_to_user_id,geo,conversation_id,created_at,lang,public_metrics,referenced_tweets,reply_settings,source',
    #                 # 'user.fields': 'id,name,username,created_at,description,public_metrics,verified',
    #                 # 'place.fields': 'full_name,id,country,country_code,geo,name,place_type',
    #                 'next_token': {}}
    
    # #Querry params for Tweet searchs
    # query_params = {'ids': keyword,
    #                 'expansions': 'author_id,entities.mentions.username,in_reply_to_user_id,referenced_tweets.id,referenced_tweets.id.author_id',
    #                 'tweet.fields': 'author_id,conversation_id,created_at,id,in_reply_to_user_id,public_metrics,text',
    #                 'user.fields': 'created_at,description,id,location,name,username,verified',
    #                 'next_token': {}}
    
    #Querry params for Retweet searchs
    query_params = {'expansions': 'pinned_tweet_id',
                    'tweet.fields': 'author_id,conversation_id,created_at,id,in_reply_to_user_id,public_metrics,text',
                    'user.fields': 'created_at,description,id,location,name,username,verified',
                    'max_results': max_results}#Min 10, max 100
                    # 'pagination_token': {}
    
    return (search_url, query_params)

def connect_to_endpoint(url, headers, params, next_token = None):
    params['next_token'] = next_token   #params object received from create_url function
    response = requests.request("GET", url, headers = headers, params = params)
    print("Endpoint Response Code: " + str(response.status_code))
    if response.status_code != 200: #-100 processing, -200 is successfull, -300 is client errors, -400 is server error
        raise Exception(
            "Request returned an error: {} {}".format(response.status_code,response.text)
        )
    return response.json()

def append_to_csv(json_response, fileName):
    #A counter variable
    counter = 0
    #Open OR create the target CSV file
    csvFile = open(fileName, "a", newline="", encoding='utf-8')
    csvWriter = csv.writer(csvFile)
    
    #Loop through each tweet
    for tweet in json_response['data']:
        # 1. Author ID
        author_id = tweet['author_id']

        # 2. Time created
        created_at = dateutil.parser.parse(tweet['created_at'])

        # 3. Geolocation
        if ('geo' in tweet):   
            geo = tweet['geo']['place_id']
        else:
            geo = " "

        # 4. Tweet ID
        tweet_id = tweet['id']

        # 5. Language
        lang = tweet['lang']

        # 6. Tweet metrics
        retweet_count = tweet['public_metrics']['retweet_count']
        reply_count = tweet['public_metrics']['reply_count']
        like_count = tweet['public_metrics']['like_count']
        quote_count = tweet['public_metrics']['quote_count']

        # 7. source
        source = tweet['source']

        # 8. Tweet text
        text = tweet['text']
        
        # Assemble all data in a list
        res = [author_id, created_at, geo, tweet_id, lang, like_count, quote_count, reply_count, retweet_count, source, text]
        
        # Append the result to the CSV file
        csvWriter.writerow(res)
        counter += 1

    # When done, close the CSV file
    csvFile.close()

    # Print the number of tweets for this iteration
    print("# of Tweets added from this response: ", counter) 
def main():
    # #Inputs for the request
    # os.environ['TOKEN'] = 'AAAAAAAAAAAAAAAAAAAAACNMYQEAAAAADF5%2Fp5%2Fw%2FRW1OhMju0XsTjTa%2F%2FQ%3DPQT9mLoy3xLgo1T0h1oeOPqWoXbuHhfwTdwPFrmxET6teLcsG1'
    # bearer_token = auth()
    # headers = create_headers(bearer_token)
    # keyword = "bitcoin lang:en"
    # start_time = "2022-01-18T14:26:00.000Z"
    # end_time =   "2022-01-23T09:37:00.000Z"
    # max_results = 15

    # url = create_url(keyword,start_time,end_time,max_results)
    # json_response= connect_to_endpoint(url[0],headers,url[1]);
    # print(json.dumps(json_response, indent=4, sort_keys=True))
    # #Save result to JSON file
    # with open("twit_data.json",'w') as f:
    #     json.dump(json_response, f)
    # print("end")
    a=1

if __name__ == '__main__':
    main()
    os.environ['TOKEN'] = 'AAAAAAAAAAAAAAAAAAAAACNMYQEAAAAADF5%2Fp5%2Fw%2FRW1OhMju0XsTjTa%2F%2FQ%3DPQT9mLoy3xLgo1T0h1oeOPqWoXbuHhfwTdwPFrmxET6teLcsG1'
    #URL Authentication and querry process
    bearer_token = auth()
    headers = create_headers(bearer_token)
    # First keyword for vaccination status with original tweets
    # keyword = "#covid19 #vaccination lang:en -is:retweet -is:reply -is:quote"
    #Second keyword for retweets of each original tweets
    keyword = "1485136020505243650"
    # start_time = "2022-01-18T14:26:00.000Z"
    end_time =   "2022-01-23T09:37:00.000Z"
    max_results = 10
    #original url
    # url = create_url(keyword,start_time,end_time,max_results)
    url = create_url(keyword,None,None ,max_results)
    #Receive JSON file for such request
    json_response= connect_to_endpoint(url[0],headers,url[1]);
    #Debug "Tweets" data from JASON object
    # print(json.dumps(json_response[0], indent=4, sort_keys=True))
    
    # #Code to write JSON into csv file
    # csvFile = open("twitter_data.csv", "a", newline="", encoding='utf-8')
    # csvWriter = csv.writer(csvFile)
    # #Create headers columns for our specified dataset
    # csvWriter.writerow(['author id', 'created_at', 'geo', 'id','lang', 'like_count', 'quote_count', 'reply_count','retweet_count','source','tweet'])
    # csvFile.close()

    print("end")
    #Write to data file
    # df = pd.DataFrame(json_response['data'])
    # df.to_csv('twitter_data.csv')