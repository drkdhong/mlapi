#import json
from flask import Blueprint, jsonify, request
from api import calculation, preparation
#from .json_validate import validate_json, validate_schema
api = Blueprint("api", __name__, url_prefix="/v1")

@api.get('/')
def hello_world():
    return 'Hello, World!'
    
@api.post("/file-id")
def file_id():
    return preparation.insert_filenames(request)

@api.post("/probabilities")
def probabilities():
    return calculation.evaluate_probs(request)
