"""
    All routing/endpoint functionalities
"""

from flask import request, Request

from encoding import json_to_resqml, write_dict_to_zip_stream
from zipfile import ZipFile
from io import BytesIO

from fmu.sumo.explorer import Explorer



def check_request_to_token(request : Request) -> str:
    """
        Check that a request is formatted correctly and return the auth token if it exists.
        Throws exception on error.
    """
    token = request.headers.get("Authorization")
    if not token:
        raise Exception("Missing authorization token in header", 401)
    
    token = token.split(" ")[1]
    return token


def get_objects() -> str:
    """
        Retrieve all unfiltered metadata for a given object.
    """
    try:
        token = check_request_to_token(request)
    except Exception as e:
        return e

    sumo = Explorer("dev", token)

    uuid = request.args.get("id")
    if not uuid:
        return "Missing object id", 400

    try:
        metadata = sumo._utils.get_object(uuid)
    except Exception as e:
        return f"{e} while searching for object:'{uuid}'.\n\nUse POST for retrieving several objects", 404
    
    return json_to_resqml(metadata)


def get_several_objects() -> bytes:
    """
        Retrieve all unfiltered metadata for several given objects.
    """
    try:
        token = check_request_to_token(request)
    except Exception as e:
        return e
    
    sumo = Explorer("dev", token)

    ids = request.form.get("ids")
    if not ids:
        return "Missing object ids", 400

    zipstream = BytesIO()
    with ZipFile(zipstream, "w") as zip:
        for uuid in ids.split(";"):
            if not uuid: # Id string is empty
                continue

            try:
                metadata = sumo._utils.get_object(uuid)
            except Exception as e:
                return f"'{e}' while searching for object:'{uuid}'.", 404
        
            write_dict_to_zip_stream(metadata, zip, uuid+".resqml")

    output = zipstream.getvalue()
    zipstream.close()

    return output


def get_objects_hdf() -> bytes:
    """
        Retrieve blob data as hdf5 for a given object
    """
    return None