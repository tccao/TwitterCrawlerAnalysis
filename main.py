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
    #First using search url API to pull interested keyword
    search_url = "https://api.twitter.com/2/tweets/search/recent"

    #The params that we want to use
    query_params = {'query': keyword,
                    'start_time': start_date,
                    'end_time': end_date,
                    'max_results': max_results,#Min 10, max 100
                    'expansions': 'author_id,in_reply_to_user_id,geo.place_id',
                    'tweet.fields': 'id,text,author_id,in_reply_to_user_id,geo,conversation_id,created_at,lang,public_metrics,referenced_tweets,reply_settings,source',
                    'user.fields': 'id,name,username,created_at,description,public_metrics,verified',
                    'place.fields': 'full_name,id,country,country_code,geo,name,place_type',
                    'next_token': {}}
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

def main():
    #Inputs for the request
    # os.environ['TOKEN'] = 'AAAAAAAAAAAAAAAAAAAAACNMYQEAAAAADF5%2Fp5%2Fw%2FRW1OhMju0XsTjTa%2F%2FQ%3DPQT9mLoy3xLgo1T0h1oeOPqWoXbuHhfwTdwPFrmxET6teLcsG1'
    bearer_token = auth()
    headers = create_headers(bearer_token)
    keyword = "bitcoin lang:en"
    start_time = "2022-01-17T14:26:00.000Z"
    end_time =   "2022-01-23T09:37:00.000Z"
    max_results = 15

    url = create_url(keyword,start_time,end_time,max_results)
    json_response= connect_to_endpoint(url[0],headers,url[1]);
    print(json.dumps(json_response, indent=4, sort_keys=True))
    print("end")

if __name__ == '__main__':
    main()
