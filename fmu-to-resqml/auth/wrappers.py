"""
    All auth wrapper functions
"""

import jwt
from os import environ
from time import time
from flask import request

from auth.exchange import get_bearer_token



def verify_token(func : any) -> any:
    """
        Wrapper that verifies that a auth token exists and is valid
    """
    def wrapper(*args, **kwargs):
        token = get_bearer_token(request)
        payload = jwt.decode(token, options={"verify_signature": False})
    
        audience = payload["aud"]
        issuer = payload["iss"]
        scope = payload["scp"]
        expires = payload["exp"]

        raise Exception(payload)

        # Verify that the audience, issuer and scope is correct
        if audience.removeprefix("api://") != environ.get("AZURE_CLIENT_ID"):
            raise Exception("Token is not valid: Invalid audience", 401)
        
        if issuer != f"https://sts.windows.net/{environ.get('AZURE_TENANT_ID')}/":
            raise Exception("Token is not valid: Invalid issure", 401)
        
        if scope != "RESQML.Read":
            raise Exception("Token is not valid: Invalid scope", 401)

        # Verify that token expires in (at least) over 2 minutes
        if expires < time() - 120:
            raise Exception("Token is not valid: Expired token", 401)

        return func(*args, **kwargs)

    return wrapper