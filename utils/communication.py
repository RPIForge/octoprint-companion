import requests

def get_request(url,payload=None, header=None):
    try:
        response = requests.get(url, params=payload, headers=header)
        if(response.status_code!=200):
            return None
        return response
    except:
        return None
    
def post_request(url,paramaters=None,header=None, data=None):
    try:
        return requests.post(url, params=paramaters,  headers=header, data=data)
    except:
        return None
    
    
  
def get_json(url,payload=None, header=None):
    response = get_request(url,payload,header)
    if(response):
        return response.json()
    return None
    
    
def get_file(url,payload=None, header=None):
    request = get_request(url,None,header)
    if(request!=None):
        return request.content
        
    return None
    
