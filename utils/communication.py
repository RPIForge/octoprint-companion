import requests

def get_request(url,payload=None):
    return requests.get(url, params=payload)
    
def post_request(url,payload=None,data=None):
    return requests.get(url, params=payload, data=data)