from flask import Blueprint
import json

endpoints = Blueprint("generic_ep",__name__)

@endpoints.route('/health-check')
def health_check():
    return {'health':'pass'}