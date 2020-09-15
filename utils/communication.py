import requests

def get_request(url,payload=None):
    response = requests.get(url, params=payload)
    if(response.status_code!=200):
        return None
    return response.json()
    
def get_file(url,payload=None):
    request = get_request(url,payload)
    if(request!=None):
        return request.content
    return None
    
def post_request(url,payload=None,data=None):
    return requests.get(url, params=payload, data=data)