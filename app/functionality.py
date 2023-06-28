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
        Check that a request is contains a token and returns said auth token if it exists.
        Throws exception otherwise.
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

    uuids = request.form.get("ids")
    if not uuids:
        return "Missing object ids", 400

    zipstream = BytesIO()
    with ZipFile(zipstream, "w") as zip:
        for uuid in uuids.split(";"):
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

    match metadata["_source"]["class"]:
        case "polygons":
            return sumo.get_polygons_by_uuid(uuid).blob
        case "surface":
            return sumo.get_surface_by_uuid(uuid).blob
        case "table":
            return sumo.get_table_by_uuid(uuid).blob
        case _:
            return f"Data retrieval of {metadata['_source']['class']} currently not supported", 404