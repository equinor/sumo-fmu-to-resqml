"""
    All routing/endpoint functionalities
"""

from flask import request, Request

from zipfile import ZipFile
from io import BytesIO

from fmu.sumo.explorer import Explorer


def check_request_to_token(request : Request) -> str:
    """
        Check that a request is contains a token and returns said auth token if it exists.
        Throws exception otherwise.
    """
    token = request.headers.get("Authorization")
    if not token:
        raise Exception("Missing authorization token in header", 401)
    
    token = token.split(" ")[1]
    return token


def get_resqml():
    " Get the RESQML data of given objects. This includes both EPC and H5 files. "
    pass