import requests

def get_request(url,payload=None, header=None):
    
    response = requests.get(url, params=payload, headers=header)

    if(response.status_code!=200):
        return None
    return response

def post_request(url,paramaters=None,header=None, data=None):
    return requests.post(url, params=paramaters,  headers=header, data=data)
    
    
  
def get_json(url,payload=None, header=None):
    return get_request(url,payload,header).json()
    
def get_file(url,payload=None, header=None):
    request = get_request(url,None,header)
    if(request!=None):
        return request.content
        
    return None
    
