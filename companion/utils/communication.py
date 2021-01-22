#
# Communication file. This file stores all methods that deal with HTTP requests
#

import requests
import logging


def get_request(url,payload=None, header=None):
    log = logging.getLogger('general_logger')
    try:
        
        response = requests.get(url, params=payload, headers=header)
        log.debug("get response from {} code: {} content: {}".format(url, response.status_code,response.content))
        
        if(response.status_code!=200):
            log.error('get failed from {} code: {}'.format(url, response.status_code))
            return None
        return response
    except Exception as e:
        log.error("get request failed")
        log.error(e)
        return None
    
def post_request(url,paramaters=None,header=None, data=None):
    log = logging.getLogger('general_logger')
    try:
        
        response = requests.post(url, params=paramaters,  headers=header, data=data)
        log.debug("post response from {} code: {} content: {}".format(url, response.status_code,response.content))
        
        if(response.status_code!=200):
            log.error('post failed from {} code: {}'.format(url, response.status_code))
            return None
        return response
        
    except Exception as e:
        log.error("post request failed")
        log.error(e)
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
