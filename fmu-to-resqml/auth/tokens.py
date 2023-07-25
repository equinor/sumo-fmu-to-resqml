"""
    All functions managing tokens
"""

import jwt
import json
import requests

from time import time
from os import environ

from flask import Request



def get_bearer_token(request : Request) -> str:
    token = request.headers["Authorization"]
    if not token:
        raise Exception("Missing authorization token in header", 401)
    
    try:
        token = token.split("Bearer ")[1]
    except:
        raise Exception("Authorization token must be on the form: 'Bearer <token>'", 401)
    
    return token