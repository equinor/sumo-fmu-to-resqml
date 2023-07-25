"""
    All auth wrapper functions
"""

import jwt
from time import time
from flask import request

from auth.tokens import get_bearer_token


def verify_token(func : any) -> any:
    """
        Wrapper that verifies that a auth token exists and is valid
    """
    def wrapper(*args, **kwargs):
        token = get_bearer_token(request)
    
        expires = jwt.decode(token, options={"verify_signature": False})['exp']

        # Verify that token expires in (at least) over 2 minutes
        if expires < time() - 120:
            raise Exception("Access_token has expired", 401)

        return func(*args, **kwargs)

    return wrapper