"""
    All routing/endpoint functionalities
"""

from flask import request, Request

from encoding import json_to_resqml, write_dict_to_zip_stream, blobs_to_hdf5
from zipfile import ZipFile
from io import BytesIO
from warnings import warn

from fmu.sumo.explorer import Explorer

# Deprecation warning decorator
def deprecated(func):
    warn(f"Function {func.__name__} is deprecated.")
    return func


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

@deprecated
def get_objects() -> str:
    """
        Retrieve all unfiltered metadata for a given object.
    """
    try:
        token = check_request_to_token(request)
    except Exception as e:
        return e.args

    sumo = Explorer("dev", token)

    uuid = request.args.get("id")
    if not uuid:
        return "Missing object id", 400

    try:
        metadata = sumo._utils.get_object(uuid)
    except Exception as e:
        return f"Error: {e}, while searching for object:'{uuid}'.\n\nUse POST for retrieving several objects", 404
    
    return json_to_resqml(metadata)

@deprecated
def get_several_objects() -> bytes:
    """
        Retrieve all unfiltered metadata for several given objects.
    """
    try:
        token = check_request_to_token(request)
    except Exception as e:
        return e.args
    
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
                return f"Error: {e}, while searching for object:'{uuid}'.", 404
        
            write_dict_to_zip_stream(metadata, zip, uuid+".resqml")

    return zipstream.getvalue()

@deprecated
def get_objects_hdf() -> bytes:
    """
        Retrieve blob data as hdf5 for a given object
    """
    try:
        token = check_request_to_token(request)
    except Exception as e:
        return e.args
    
    sumo = Explorer("dev", token)

    uuid = request.args.get("id")
    if not uuid:
        return "Missing object id", 400
    
    try:
        metadata = sumo._utils.get_object(uuid)
    except Exception as e:
        return f"Error: {e}, while searching for object:'{uuid}'.\n\nUse POST for retrieving several objects", 404

    object_type = metadata["_source"]["class"]
    match object_type:
        case "polygons":
            blob = sumo.get_polygons_by_uuid(uuid).blob
        case "surface":
            blob = sumo.get_surface_by_uuid(uuid).blob
        case "table":
            blob = sumo.get_table_by_uuid(uuid).blob
        case _:
            return f"Data retrieval of {object_type} currently not supported", 404
        
    return blobs_to_hdf5([blob], [object_type])

@deprecated
def get_several_objects_hdf() -> bytes:
    """
        Retrieve blob data as hdf5 for several objects
    """
    try:
        token = check_request_to_token(request)
    except Exception as e:
        return e.args
    
    sumo = Explorer("dev", token)

    uuids = request.form.get("ids")
    if not uuids:
        return "Missing object ids", 400
    
    blobs, object_types = [], []
    for uuid in uuids.split(";"):
        try:
            metadata = sumo._utils.get_object(uuid)
        except Exception as e:
            return f"Error: {e}, while searching for object:'{uuid}'", 404

        object_type = metadata["_source"]["class"]
        match object_type:
            case "polygons":
                blob = sumo.get_polygons_by_uuid(uuid).blob
            case "surface":
                blob = sumo.get_surface_by_uuid(uuid).blob
            case "table":
                blob = sumo.get_table_by_uuid(uuid).blob
            case _:
                return f"Data retrieval of {object_type} currently not supported", 404
        
        blobs.append(blob)
        object_types.append(object_type)
        
    return blobs_to_hdf5(blobs, object_types)