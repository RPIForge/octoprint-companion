from flask import Blueprint, Response, request
from utils.variable import variable_instance
import json

endpoints = Blueprint("generic_ep",__name__)

@endpoints.route('/health-check')
def health_check():
    return {'health':'pass'}



@endpoints.route('/probe')
def probe():
    return Response(variable_instance.mtconnect.probe(), mimetype='text/xml')

@endpoints.route('/current', defaults={'identifier': None})
@endpoints.route('/<identifier>/current')
def current(identifier):
    path = request.args.get('path', None)
    at = request.args.get('at', None)
 
    try:
        at = int(at)
    except:
        pass

    if(identifier is not None):
        path = ".//*[@id='{}'] | .//*[@name='{}']".format(identifier,identifier)

    response = Response(variable_instance.mtconnect.current(at, path), mimetype='text/xml')
    return response

@endpoints.route('/sample', defaults={'identifier': None})
@endpoints.route('/<identifier>/sample')
def sample(identifier):
    path = request.args.get('path', None)
    start = request.args.get('from', None)
    count = request.args.get('count',None)

    try:
        at = int(at)
    except:
        pass

    try:
        count = int(count)
    except:
        pass 
    
    try:
        start = int(start)
    except:
        pass
    
    if(identifier is not None):
        path = ".//*[@id='{}'] | .//*[@name='{}']".format(identifier,identifier)

    response = Response(variable_instance.mtconnect.sample(path,start,count), mimetype='text/xml')
    return response


