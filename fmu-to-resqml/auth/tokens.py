"""
    All functions managing tokens
"""

import jwt
import json
import requests

from time import time
from os import environ

from flask import Request



def get_token_from_file() -> str:
    """
        Retrieve the Azure Federated Token from its file
    """
    with open(environ.get("AZURE_FEDERATED_TOKEN_FILE"), "r") as f:
        token = f.read()
    return token


def get_bearer_token(request : Request) -> str:
    """
        Retrieve the bearer token from a request
    """
    token = request.headers["Authorization"]
    if not token:
        raise Exception("Missing authorization token in header", 401)
    
    try:
        token = token.split("Bearer ")[1]
    except:
        raise Exception("Authorization token must be on the form: 'Bearer <token>'", 401)
    
    return token


def get_exchange_token(bearer_token : str, client_auth : dict) -> str:
    """
        Retrieves an exchange token given bearer token and client auth
    """
    if not bearer_token:
        raise Exception("Empty bearer token", 401)
    if not client_auth["config"]["client_id"]:
        raise Exception("Empty client ID in client_auth", 500)
    if not client_auth["config"]["scope"]:
        raise Exception("Empty scope in client_auth", 500)
    if not client_auth["token"]:
        raise Exception("Empty federated token in client_auth", 500)
    
    # Copied directly from aggregation service
    url_values = {
        "grant_type": "urn:ietf:params:oauth:grant-type:jwt-bearer",
        "client_id": client_auth["config"]["client_id"],
        "client_assertion_type": "urn:ietf:params:oauth:client-assertion-type:jwt-bearer",
        "client_assertion": client_auth["token"],
        "scope": client_auth["config"]["scope"],
        "requested_token_use": "on_behalf_of",
        "assertion": bearer_token,
    }

    try:
        response = requests.post(client_auth["config"]["endpoint"]["token_url"], url_values).json()
        token = response["access_token"]
    except Exception as e:
        raise Exception("Error on token-url POST:" + e, 500)
    
    return token


def get_exchange_token_alg(request : Request, environment : str) -> str:
    """
        Retrieves an exchange token given a request and an environment
    """

    # TODO: Values are currently empty
    scopes = {
        "preview": "",
        "dev": "",
        "test": "",
        "prod": ""
    }

    client_auth = {
        "token": get_token_from_file(),
        "config": {
            "client_id": environ.get("AZURE_CLIENT_ID"),
            "scope": scopes[environment],
            "endpoint": {
                "token_url": f"{environ.get('AZURE_AUTHORITY_HOST')}{environ.get('AZURE_TENANT_ID')}/oauth2/v2.0/token"
            }
        }
    }

    bearer_token = get_bearer_token()
    exchange_token = get_exchange_token(bearer_token, client_auth)

    return exchange_token