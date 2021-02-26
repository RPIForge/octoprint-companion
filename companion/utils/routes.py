from flask import Blueprint, Response
from utils.variable import variable_instance
import json

endpoints = Blueprint("generic_ep",__name__)

@endpoints.route('/health-check')
def health_check():
    return {'health':'pass'}


@endpoints.route('/probe')
def probe():
    return Response(variable_instance.mtconnect.probe(), mimetype='text/xml')