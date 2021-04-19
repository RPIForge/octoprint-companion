from flask import Blueprint, Response, request
from utils.variable import variable_instance
import json
from datetime import datetime

endpoints = Blueprint("generic_ep",__name__)

@endpoints.route('/health-check')
def health_check():
    differnce = datetime.now() - variable_instance.last_update
    if(differnce.total_seconds()>120):
        return Response({'health':'error'}, status=500)

    return {'health':'pass'}



@endpoints.route('/probe')
def probe():
    response = variable_instance.mtconnect.probe()
    return Response(response.get_xml(),status=response.get_status(), mimetype='text/xml')

@endpoints.route('/current', defaults={'identifier': None})
@endpoints.route('/<identifier>/current')
def current(identifier):
    path = request.args.get('path', None)
    at = request.args.get('at', None, type=int)

    if(identifier is not None):
        path = ".//*[@id='{}'] | .//*[@name='{}']".format(identifier,identifier)

    response = variable_instance.mtconnect.current(at, path)
    return Response(response.get_xml(),status=response.get_status(), mimetype='text/xml')

@endpoints.route('/sample', defaults={'identifier': None})
@endpoints.route('/<identifier>/sample')
def sample(identifier):
    path = request.args.get('path', None)
    start = request.args.get('from', None, type=int)
    count = request.args.get('count',None, type=int)

    if(identifier is not None):
        path = ".//*[@id='{}'] | .//*[@name='{}']".format(identifier,identifier)

    response = variable_instance.mtconnect.sample(path,start,count)
    return Response(response.get_xml(),status=response.get_status(), mimetype='text/xml')
