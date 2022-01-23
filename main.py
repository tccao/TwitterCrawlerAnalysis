from configurs import *
load_dotenv()

#Export bearer_token to set environment variables
bearer_token = os.environ.get("BEARER_TOKEN")

def main():
    #Inputs for the request
    bearer_token = auth()
    headers = create_headers(bearer_token)
    keyword = "bitcoin lang:en"
    start_time = "2021-11-01T09:37:00.000Z"
    end_time = "2022-01-23T09:37:00.000Z"
    max_results = 15

    url = create_url(keyword,start_time,end_time,max_results)
    json_response= connect_to_endpoint(url[0],headers,url[1]);
    print(json.dumps(json_response, indent=4, sort_keys=True))

    if __name__ == '__main__':
        main()
