"""
    All routing/endpoint functionalities
"""

import jwt

from flask import request, Request, Response

from zipfile import ZipFile
from io import BytesIO

from utility import convert_object_to_resqml, convert_objects_to_resqml, convert_ensemble_to_resqml

from fmu.sumo.explorer import Explorer

from time import time


def try_get_token(request : Request) -> str:
    """
        Try to retrieve an access token from the request.
        Returns the token if it exists, raises exception otherwise.
    """
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
    if request.method == "POST":
        uuids = request.form.get("uuids")
        if not uuids:
            return "Missing object uuids", 400
        uuids = uuids.split(";")
    
        epcstream, hdfstream = convert_objects_to_resqml(uuids, sumo)
    else:
        uuid = request.args.get("uuid")
        if not uuid:
            return "Missing object uuid", 400
        
        epcstream, hdfstream = convert_objects_to_resqml([uuid], sumo)

    # Zip together both streams
    zipstream = BytesIO()
    with ZipFile(zipstream, "w") as zip:
        zip.writestr("epc.zip", epcstream.getvalue())
        zip.writestr("hdf.zip", hdfstream.getvalue())

    # Return the byte value of the zip stream
    return zipstream.getvalue(), 200


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
    if request.method == "POST":
        uuids = request.form.get("uuids")
        if not uuids:
            return "Missing object uuids", 400
        uuids = uuids.split(";")

        epcstream, _ = convert_objects_to_resqml(uuids, sumo)
    else:
        uuid = request.args.get("uuid")
        if not uuid:
            return "Missing object uuid", 400
        
        epcstream, _ = convert_object_to_resqml(uuid, sumo)
    
    # Return the byte value of the epc stream
    return epcstream.getvalue(), 200


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
    if request.method == "POST":
        uuids = request.form.get("uuids")
        if not uuids:
            return "Missing object uuids", 400
        uuids = uuids.split(";")

        _, hdfstream = convert_objects_to_resqml(uuids, sumo)
    else:
        uuid = request.args.get("uuid")
        if not uuid:
            return "Missing object uuid", 400
        
        _, hdfstream = convert_object_to_resqml(uuid, sumo)
    
    # Return the byte value of the hdf stream
    return hdfstream.getvalue(), 200


def get_ensemble() -> bytes:
    """
        Retrieve an EPC and HDF5 file of all realizations given case ID and iteration number.

        Always returns zipped data, as EPC and HDF5 always come together.
    """

    # Retrieve the access token from the request, and intialize the sumo explorer
    try:
        token = try_get_token(request)
    except Exception as e:
        return e.args
    sumo = Explorer("dev", token)

    # Retrieve case id from the request
    uuid = request.form.get("uuid")

    # Retrieve filter information from request
    iterations = request.form.get("iter").split(";")
    tagnames = request.form.get("tags").split(";")
    names = request.form.get("name").split(";")

    # Convert and get the epc and hdf stream containing the wanted data in RESQML format
    epcstream, hdfstream = convert_ensemble_to_resqml(uuid, iterations, tagnames, names, sumo)

    # Open a stream to contain the zip data
    zipstream = BytesIO()

    # Zip together these two files
    with ZipFile(zipstream, "w") as zip:
        zip.writestr(f"{uuid}.epc", epcstream.getvalue())
        zip.writestr(f"{uuid}.h5", hdfstream.getvalue())

    # Output the zip stream
    return zipstream

def get_ensemble_epc() -> bytes:
    """
        Retrieve an EPC file of all realizations given case ID and iteration number.

        Returns an unzipped EPC file.
    """
    return "Not implemented yet", 501

def get_ensemble_hdf() -> bytes:
    """
        Retrieve an HDF5 file of all realizations given case ID and iteration number.

        Returns an unzipped HDF5 file.
    """
    return "Not implemented yet", 501