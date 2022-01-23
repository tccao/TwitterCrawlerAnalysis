def connect_to_endpoint(url, headers, params, next_token = None):
    params['next_token'] = next_token   #params object received from create_url function
    response = requests.request("GET", url, headers = headers, params = params)
    print("Endpoint Response Code: " + str(response.status_code))
    if response.status_code != 200: #-100 processing, -200 is successfull, -300 is client errors, -400 is server error
        raise Exception(response.status_code, response.text)
    return response.json()
