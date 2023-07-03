"""
    All routing/endpoint functionalities
"""

from flask import request, Request

from zipfile import ZipFile
from io import BytesIO

from fmu.sumo.explorer import Explorer


def try_get_token(request : Request) -> str:
    """
        Try to retrieve an access token from the request.
        Returns the token if it exists, raises exception otherwise.
    """
    token = request.headers.get("Authorization")
    if not token:
        raise Exception("Missing authorization token in header", 401)
    
    token = token.split(" ")[1]
    return token


def get_resqml() -> bytes:
    """
        Get the RESQML data of given objects. This includes both EPC and H5 files.

        Always returns zipped data, as EPC and H5 always come together.
    """

    # Retrieve the access token from the request, and intialize the sumo explorer
    try:
        token = try_get_token(request)
    except Exception as e:
        return e.args
    sumo = Explorer("dev", token)

    # Retrieve the given object uuids from the request
    uuids = request.args.get("uuids")
    if not uuids:
        return "Missing object uuids", 400
    

    return "Endpoint not implemented yet", 501


def get_epc() -> bytes:
    """
        Get only the EPC files of given objects.

        Returned zipped if requesting for several objects, unzipped otherwise.
    """

    # Retrieve the access token from the request, and intialize the sumo explorer
    try:
        token = try_get_token(request)
    except Exception as e:
        return e.args
    sumo = Explorer("dev", token)

    # Retrieve the given object uuids from the request
    uuids = request.args.get("uuids")
    if not uuids:
        return "Missing object uuids", 400
    

    return "Endpoint not implemented yet", 501


def get_hdf() -> bytes:
    """
        Get only the H5 files of given objects.

        Returned zipped if requesting for several objects, unzipped otherwise.
    """

    # Retrieve the access token from the request, and intialize the sumo explorer
    try:
        token = try_get_token(request)
    except Exception as e:
        return e.args
    sumo = Explorer("dev", token)

    # Retrieve the given object uuids from the request
    uuids = request.args.get("uuids")
    if not uuids:
        return "Missing object uuids", 400
    

    return "Endpoint not implemented yet", 501