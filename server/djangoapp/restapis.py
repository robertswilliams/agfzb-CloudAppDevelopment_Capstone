import requests
import json
# import related models here
from .models import CarDealer, DealerReview
from requests.auth import HTTPBasicAuth

# Create a `get_request` to make HTTP GET requests
# e.g., response = requests.get(url, params=params, headers={'Content-Type': 'application/json'},
#                                     auth=HTTPBasicAuth('apikey', api_key))
def get_request(url, **kwargs):
    print(kwargs)
    print("GET from {} ".format(url))
    api_key = None
    if 'api_key' in kwargs:
        api_key = kwargs["api_key"]
        params = dict()
        params["text"] = kwargs["text"]
        params["version"] = kwargs["version"]
        params["features"] = kwargs["features"]
        params["language"] = kwargs["language"]
        params["return_analyzed_text"] = kwargs["return_analyzed_text"]
 
    header={'Content-Type': 'application/json'}
    try:
        # Call get method of requests library with URL and parameters
        #response = requests.get(url, headers={'Content-Type': 'application/json'},
        #                            params=kwargs)
        if api_key:
            print('api_key: ' + api_key)
            # Basic authentication GET
            response = requests.get(url, params=params, headers=header, auth=HTTPBasicAuth('apikey', api_key))
        else:
           # no authentication GET
            response = requests.get(url, headers=header, params=kwargs)
    except:
        # If any error occurs
        print("Network exception occurred")
    status_code = response.status_code
    print("With status {} ".format(status_code))
    json_data = json.loads(response.text)
    return json_data

# Create a `post_request` to make HTTP POST requests
# e.g., response = requests.post(url, params=kwargs, json=payload)
def post_request(url, payload, **kwargs):
    print(kwargs)
    print("POST to {} ".format(url))
    api_key = None
 
    try:
        # Call post method of requests library with URL and parameters
        response = requests.post(url, params=kwargs, json=payload)
    except:
        # If any error occurs
        print("Network exception occurred")
    status_code = response.status_code
    print("With status {} ".format(status_code))
    #json_data = json.loads(response.text)
    return status_code

# Create a get_dealers_from_cf method to get dealers from a cloud function
# def get_dealers_from_cf(url, **kwargs):
# - Call get_request() with specified arguments
# - Parse JSON results into a CarDealer object list
def get_dealers_from_cf(url, **kwargs):
    results = []
    # Call get_request with a URL parameter
    json_result = get_request(url)
    if json_result:
        #print("results: ")
        #print(json_result)
        # Get the row list in JSON as dealers
        dealers = json_result["action_results"]
        # For each dealer object
        for dealer_doc in dealers:
            # Create a CarDealer object with values in `doc` object
            dealer_obj = CarDealer(address=dealer_doc["address"], city=dealer_doc["city"], full_name=dealer_doc["full_name"],
                                   id=dealer_doc["id"], lat=dealer_doc["lat"], long=dealer_doc["long"],
                                   short_name=dealer_doc["short_name"],
                                   st=dealer_doc["st"], zip=dealer_doc["zip"])
            results.append(dealer_obj)

    return results

# Create a get_dealer_reviews_from_cf method to get reviews by dealer id from a cloud function
# def get_dealer_by_id_from_cf(url, dealerId):
# - Call get_request() with specified arguments
# - Parse JSON results into a DealerView object list
def get_dealer_reviews_from_cf(url, **kwargs):
    results = []
    # Call get_request with a URL parameter
    json_result = get_request(url, **kwargs)
    if json_result:
        print("results: ")
        print(json_result)
        if not 'action-result' in json_result:
            return results
        # Get the row list in JSON as dealers
        reviews = json_result["action-result"]
        # For each dealer object
        for review in reviews:
            # Create a CarDealer object with values in `doc` object
            purchase = review["purchase"]
            make = review["car_make"] if purchase else None
            model = review["car_model"] if purchase else None
            year = review["car_year"] if purchase else None
            purchase_date = review["purchase_date"] if purchase else None
            # pull year out of purchase date, so it can be displayed properly
            if purchase_date:
                purchase_date_list = purchase_date.split('/')
                if len(purchase_date_list) >= 3:
                    purchase_date = purchase_date_list[2]
            sentiment = analyze_review_sentiments(review["review"])
            dealer_obj = DealerReview(dealership=review["dealership"], name=review["name"], purchase=purchase,
                                   review=review["review"],
                                   id=review["id"],
                                   sentiment=sentiment,
                                   purchase_date=purchase_date,
                                   car_make=make,
                                   car_model=model,
                                   car_year=year)
            results.append(dealer_obj)

    return results



# Create an `analyze_review_sentiments` method to call Watson NLU and analyze text
def analyze_review_sentiments(text):
# - Call get_request() with specified arguments
# - Get the returned sentiment label such as Positive or Negative
    params = dict()
    params["api_key"] = 'mdmtKlDZfzMi7E3NHWK-ZDQydsDm4WEAdPqLTnYZrKk7'
    params["text"] = text
    params["version"] = '2021-03-25'
    params["features"] = ['sentiment']
    params["language"] = 'en'
    params["return_analyzed_text"] = False

    url = 'https://api.us-south.natural-language-understanding.watson.cloud.ibm.com/instances/5b5bbb52-07ca-4b4e-930a-c8e6f8ecd5ee//v1/analyze'
    json_result = get_request(url, **params)

    result = 'indeterminate'
    if json_result:
        print("results: ")
        print(json_result)
        sentiment = json_result["sentiment"]
        print("sentiment: ")
        print(sentiment)
        result = sentiment["document"]["label"]
 
    return result



