import requests

def get_request(url,payload=None, header=None):
    
    response = requests.get(url, params=payload, headers=header)

    if(response.status_code!=200):
        return None
    return response.json()
    
def get_file(url,payload=None, header=None):
    request = get_request(url,None,header)
    if(request!=None):
        print(request)
        return request.content
    return None
    
def post_request(url,payload=None,data=None):
    return requests.get(url, params=payload, data=data)