# For sending GET requests from the API
import requests
# For saving access tokens and for file management when creating and adding to the dataset
import os
# For dealing with json responses we receive from the API
import json
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
max_nodes=500

def auth():
    return os.getenv('TOKEN')

def create_headers(bearer_token):
    headers = {"Authorization": "Bearer {}".format(bearer_token)}
    return headers

def create_url(keyword,end_date, case, max_results = 10):
    if case == 1:
        # First using recent search url API to pull interested keyword
        search_url = "https://api.twitter.com/2/tweets/search/recent"
        # #Querry params for recent search
        query_params = {'query': keyword,
                        'end_time': end_date,
                        'max_results': max_results,#Min 10, max 100
                        #Expansion: Expands payload of ID into complete object, stores in jason['includes']
                        'expansions': 'author_id,in_reply_to_user_id,geo.place_id',
                        'tweet.fields': 'id,text,author_id,in_reply_to_user_id,geo,conversation_id,created_at,lang,public_metrics,referenced_tweets,reply_settings,source',
                        'user.fields': 'id,name,username,created_at,description,public_metrics,verified',
                        'place.fields': 'full_name,id,country,country_code,geo,name,place_type',
                        'next_token': {}}

    if case == 2:
        #Tweet search url
        search_url = "https://api.twitter.com/2/tweets"
        # #Querry params for Tweet searchs
        query_params = {'ids': keyword,
                        'expansions': 'author_id,entities.mentions.username,in_reply_to_user_id,referenced_tweets.id,referenced_tweets.id.author_id',
                        'tweet.fields': 'author_id,conversation_id,created_at,id,in_reply_to_user_id,public_metrics,text',
                        'user.fields': 'created_at,description,id,location,name,username,verified',
                        'next_token': {}}

    if case == 3:
        #Retweet search url
        search_url = "https://api.twitter.com/2/tweets/"+keyword+"/retweeted_by"
        #Querry params for Retweet searchs
        query_params = {'expansions': 'pinned_tweet_id',
                        'tweet.fields': 'author_id,conversation_id,created_at,id,in_reply_to_user_id,public_metrics,text,referenced_tweets',
                        'user.fields': 'created_at,description,id,location,name,username,verified',
                        'max_results': max_results,#Min 10, max 100
                        'pagination_token': {}}

    return (search_url, query_params)

def connect_to_endpoint(url, headers, params, case,next_token = None):
    if case==3:
        params['pagination_token'] = next_token   #params object received from create_url function
        response = requests.request("GET", url, headers = headers, params = params)
        print("Endpoint Response Code: " + str(response.status_code))
        if response.status_code != 200: #-100 processing, -200 is successfull, -300 is client errors, -400 is server error
            raise Exception(
                "Request returned an error: {} {}".format(response.status_code,response.text)
            )
        return response.json()
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
    #List of Tweet id
    tweet_id_list=[]
    #Open OR create the target CSV file
    csvFile = open(fileName, "a", newline="", encoding='utf-8')
    csvWriter = csv.writer(csvFile)

    #Loop through each tweet
    for tweet in json_response['data']:
        # Author ID
        author_id = tweet['author_id']
        # Time created
        tweet_created_at = dateutil.parser.parse(tweet['created_at'])
        # Geolocation
        if ('geo' in tweet):
            geo = tweet['geo']['place_id']
        else:
            geo = ""
        # Conversation_ID
        conversation_id = tweet['conversation_id']
        # Tweet ID
        tweet_id = tweet['id']
        tweet_id_list.append(str(tweet_id))
        # language
        lang = tweet['lang']
        # Tweet metrics
        retweet_count = tweet['public_metrics']['retweet_count']
        reply_count = tweet['public_metrics']['reply_count']
        like_count = tweet['public_metrics']['like_count']
        quote_count = tweet['public_metrics']['quote_count']
        # source
        source = tweet['source']
        # Tweet text
        text = tweet['text']

        # Assemble all data in a list
        column_headers = [author_id, tweet_created_at, geo, conversation_id, tweet_id, lang, like_count, quote_count,
                          reply_count, retweet_count, source, text]
        # Append the result to the CSV file
        csvWriter.writerow(column_headers)
        counter += 1
    # When done, close the CSV file
    csvFile.close()
    # Print the number of tweets for this iteration
    print("Number of Tweets added to file: ", counter)
    return tweet_id_list

def append_to_csv_retweet_user(ori_tweet_id,json_response, fileName):
    #A counter variable
    counter = 0
    #Open OR create the target CSV file
    csvFile = open(fileName, "a", newline="", encoding='utf-8')
    csvWriter = csv.writer(csvFile)

    #Loop through each users
    for users_data in json_response['data']:
        # Author ID
        author_id = users_data['id']
        # Name of user
        name_user = users_data['name']
        # location
        if 'location' in users_data:
            user_location = users_data['location']
        else:
            user_location=""
        # Assemble all data in a list
        column_headers = [ori_tweet_id,author_id, name_user, user_location]
        # Append the result to the CSV file
        csvWriter.writerow(column_headers)
        counter += 1

    # When done, close the CSV file
    csvFile.close()
    # Print the number of tweets for this iteration
    print("Number of retweet users added to file: ", counter)

def append_to_csv_retweet_tweets(ori_tweet_id,json_response, fileName):
    #A counter variable
    counter = 0
    #List of Tweet id
    tweet_id_list=[]
    #Open OR create the target CSV file
    csvFile = open(fileName, "a", newline="", encoding='utf-8')
    csvWriter = csv.writer(csvFile)

    #Loop through each retweet_tweets
    if 'includes' in json_response:
        for tweets in json_response['includes']['tweets']:
            # Author ID
            author_id = tweets['author_id']
            #Tweets ID
            tweets_id=tweets['id']
            tweet_id_list.append(str(tweets_id))
            # Time created
            tweets_data_created_at = dateutil.parser.parse(tweets['created_at'])
            # conversation_id
            conversation_id = tweets['conversation_id']
            if('referenced_tweets' in tweets):
                # referenced tweet id
                referenced_tweets_id = tweets['referenced_tweets'][0]['id']
                # referenced tweet type
                referenced_tweets_type = tweets['referenced_tweets'][0]['type']
            else:
                # referenced tweet id
                referenced_tweets_id = ""
                # referenced tweet type
                referenced_tweets_type = ""
            # Tweet metrics
            retweet_count = tweets['public_metrics']['retweet_count']
            reply_count = tweets['public_metrics']['reply_count']
            like_count = tweets['public_metrics']['like_count']
            quote_count = tweets['public_metrics']['quote_count']
            # Assemble all data in a list
            column_headers = [ori_tweet_id,author_id, tweets_id,tweets_data_created_at, conversation_id, referenced_tweets_id,referenced_tweets_type,retweet_count,reply_count, like_count, quote_count]
            # Append the result to the CSV file
            csvWriter.writerow(column_headers)
            counter += 1
    # When done, close the CSV file
    csvFile.close()
    # Print the number of tweets for this iteration
    print("Number of retweet tweets added to file: ", counter)
    return tweet_id_list

def main():
    os.environ['TOKEN'] = '<YOUR_BEARER_TOKEN>'
    #URL Authentication and querry process
    bearer_token = auth()
    headers = create_headers(bearer_token)

    # First keyword for vaccination status with original tweets only
    keyword = "#covid19 #vaccination lang:en -is:retweet -is:reply -is:quote"
    end_time =   "2022-01-22T00:00:01.000Z"
    #Maximum number of tweets in our analysis
    max_nodes = 500
    #Maximum number of retweet/tweets/Replies per request
    max_counts = 50
    #Number of current tweets collected so far
    no_current_tweet =0
    flag = True
    next_token = None
    count=0
    tweets_id_list=[]

    # Create file
    csvFile = open("original_tweet_data.csv", "a", newline="", encoding='utf-8')
    csvWriter = csv.writer(csvFile)
    csvWriter.writerow(['author_id','tweet_created_at','geo','conversation_id','tweet_id','language','retweet_count','reply_count','like_count,','quote_count','source','text'])
    csvFile.close()

    csvFile = open("retweet_user_data.csv", "a", newline="", encoding='utf-8')
    csvWriter = csv.writer(csvFile)
    csvWriter.writerow(['retweet_id','author_id','name_user','user_location'])
    csvFile.close()

    csvFile = open("retweet_tweets_data.csv", "a", newline="", encoding='utf-8')
    csvWriter = csv.writer(csvFile)
    csvWriter.writerow(['original_tweet_id','author_id','tweets_id','tweets_data_created_at','conversation_id','referenced_tweets_id','referenced_tweets_type','retweet_count','reply_count','like_count','quote_count'])
    csvFile.close()

    #Loop condition until we meet max_counts
    while flag:
        if count >= max_counts:
            break
        print("Token: ", next_token)
        case=1
        #original url, case=1 for recent search API
        url_tweet = create_url(keyword,end_time,case,max_counts)
        json_response_tweet = connect_to_endpoint(url_tweet[0], headers, url_tweet[1], case,next_token)
        result_count = json_response_tweet['meta']['result_count']

        if 'next_token' in json_response_tweet['meta']:
            # Save the token to use for next call
            next_token = json_response_tweet['meta']['next_token']
            print("Next Token: ", next_token)
            if result_count is not None and result_count > 0 and next_token is not None:
                temp=append_to_csv(json_response_tweet, "original_tweet_data.csv")
                tweets_id_list=tweets_id_list+(temp)
                count += result_count
                no_current_tweet += result_count
                print("Total # of Tweets added: ", no_current_tweet)
                print("-------------------")
                time.sleep(5)
        # If no next token exists
        else:
            if result_count is not None and result_count > 0:
                print("-------------------")
                temp=append_to_csv(json_response_tweet, "original_tweet_data.csv")
                tweets_id_list=tweets_id_list+(temp)
                count += result_count
                no_current_tweet += result_count
                print("Total # of Tweets added: ", no_current_tweet)
                print("-------------------")
                time.sleep(5)
            #Since this is the final request, turn flag to false to move to exit
            flag = False
            next_token = None
        time.sleep(5)

    #Reset count and starting retweet data
    retweets_id_list=[]

    for i in range(0,len(tweets_id_list)):
        count=0
        flag = True
        next_token=None
        #Loop condition until we meet max_counts
        while flag:
            if count >= max_counts or no_current_tweet>=max_nodes:
                break
            print("Token: ", next_token)
            case=3
            #retweet url, case=3 for retweet API
            url_tweet = create_url(tweets_id_list[i],None,case,max_counts)
            json_response_retweet = connect_to_endpoint(url_tweet[0], headers, url_tweet[1], case,next_token)
            result_count = json_response_retweet['meta']['result_count']

            if 'next_token' in json_response_retweet['meta']:
                # Save the token to use for next call
                next_token = json_response_retweet['meta']['next_token']
                print("Next Token: ", next_token)
                if result_count is not None and result_count > 0 and next_token is not None:
                    append_to_csv_retweet_user(tweets_id_list[i],json_response_retweet, "retweet_user_data.csv")
                    temp=append_to_csv_retweet_tweets(tweets_id_list[i],json_response_retweet, "retweet_tweets_data.csv")
                    retweets_id_list=retweets_id_list+(temp)
                    count += result_count
                    no_current_tweet += result_count
                    print("Total # of Tweets added: ", no_current_tweet)
                    print("-------------------")
                    time.sleep(5)

            # If no next token exists
            else:
                if result_count is not None and result_count > 0:
                    print("-------------------")
                    append_to_csv_retweet_user(json_response_retweet, "retweet_user_data.csv")
                    temp=append_to_csv_retweet_tweets(tweets_id_list[i],json_response_retweet, "retweet_tweets_data.csv")
                    retweets_id_list=retweets_id_list+(temp)
                    count += result_count
                    no_current_tweet += result_count
                    print("Total # of Tweets added: ", no_current_tweet)
                    print("-------------------")
                    time.sleep(5)
                #Since this is the final request, turn flag to false to move to exit
                flag = False
                next_token = None
            time.sleep(5)

if __name__ == '__main__':
    main()
