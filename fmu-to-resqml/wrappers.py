"""
    All wrapper functions
"""

import jwt

from time import time

from flask import request


def verify_token(func : any) -> any:
    """
        Wrapper that verifies that a auth token exists and is valid
    """
    def wrapper(*args, **kwargs):
        token = request.headers.get("Authorization")
        if not token:
            raise Exception("Missing authorization token in header", 401)
    
        try:
            token = token.split(" ")[1]
        except:
            raise Exception("Authorization token must be on the form: 'Bearer <token>'", 401)
    
        expires = jwt.decode(token, options={"verify_signature": False})['exp']

        # Verify that token expires in (at least) over 2 minutes
        if expires < time() - 120:
            raise Exception("Access_token has expired", 401)

        return func(*args, **kwargs)

    return wrapper


def handle_exceptions(func : any) -> any: 
    """
        Wrapper function for handling exceptions.
    """
    def wrapper(*args, **kwargs):
        try:
            # Try to return the function value
            return func(*args, **kwargs)
        except Exception as e:
            if len(e.args) <= 1:
                raise e            
            status = e.args[1]

            # If the function returns a "Not Found" or "Not Implemented" error
            if status == 404 or status == 501:
                return e.args
            
            # If not, raise the exception further
            raise e
    
    return wrapper