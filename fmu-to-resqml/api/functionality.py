"""
    All routing/endpoint functionalities
"""

from flask import request

from zipfile import ZipFile
from io import BytesIO

from api.wrappers import handle_exceptions
from api.utility import convert_object_to_resqml, convert_objects_to_resqml, convert_ensemble_to_resqml

from auth.exchange import get_explorer
from auth.wrappers import verify_token



@handle_exceptions
@verify_token
def get_resqml() -> bytes:
    """
        Get the RESQML data of given objects. This includes both EPC and H5 files.

        Always returns zipped data, as EPC and H5 always come together.
    """

    # Initialize and get the sumo exporer
    sumo = get_explorer(request)

    # Retrieve the json data from the request body
    body = request.get_json()

    # Retrieve the given object uuids from the request 
    if request.method == "POST":
        uuids = body.get("uuids")
        if not uuids:
            return "Missing object uuids", 400
    else:
        uuid = request.args.get("uuid")
        if not uuid:
            return "Missing object uuid", 400
        uuids = [uuid]

    epcstream, hdfstream = convert_objects_to_resqml(uuids, sumo)


    # Zip together both streams
    zipstream = BytesIO()
    with ZipFile(zipstream, "w") as zip, ZipFile(epcstream, "r") as epczip, ZipFile(hdfstream, "r") as hdfzip:
        for epcname in epczip.namelist():
            zip.writestr(epcname, epczip.read(epcname))
        for hdfname in hdfzip.namelist():
            zip.writestr(hdfname, hdfzip.read(hdfname))

    # Return the byte value of the zip stream
    return zipstream.getvalue(), 200


@handle_exceptions
@verify_token
def get_epc() -> bytes:
    """
        Get only the EPC files of given objects.

        Returned zipped if requesting for several objects, unzipped otherwise.
    """

    # Initialize and get the sumo exporer
    sumo = get_explorer(request)

    # Retrieve the json data from the request body
    body = request.get_json()

    # Retrieve the given object uuids from the request 
    if request.method == "POST":
        uuids = request.form.get("uuids")
        if not uuids:
            return "Missing object uuids", 400

        epcstream, _ = convert_objects_to_resqml(uuids, sumo)
    else:
        uuid = request.args.get("uuid")
        if not uuid:
            return "Missing object uuid", 400
        
        epcstream, _ = convert_object_to_resqml(uuid, sumo)
    
    # Return the byte value of the epc stream
    return epcstream.getvalue(), 200


@handle_exceptions
@verify_token
def get_hdf() -> bytes:
    """
        Get only the H5 files of given objects.

        Returned zipped if requesting for several objects, unzipped otherwise.
    """

    # Initialize and get the sumo exporer
    sumo = get_explorer(request)

    # Retrieve the json data from the request body
    body = request.get_json()

    # Retrieve the given object uuids from the request 
    if request.method == "POST":
        uuids = request.form.get("uuids")
        if not uuids:
            return "Missing object uuids", 400

        _, hdfstream = convert_objects_to_resqml(uuids, sumo)
    else:
        uuid = request.args.get("uuid")
        if not uuid:
            return "Missing object uuid", 400
        
        _, hdfstream = convert_object_to_resqml(uuid, sumo)
    
    # Return the byte value of the hdf stream
    return hdfstream.getvalue(), 200


@handle_exceptions
@verify_token
def get_ensemble() -> bytes:
    """
        Retrieve an EPC and HDF5 file of all realizations given case ID and iteration number.

        Always returns zipped data, as EPC and HDF5 always come together.
    """

    # Initialize and get the sumo exporer
    sumo = get_explorer(request)

    # Retrieve the json data from the request body
    body = request.get_json()

    # Retrieve case id from the request
    uuid = body.get("uuid")
    if not uuid:
        return "Missing object uuid", 400

    # Retrieve filter information from request
    iterations = body.get("iter")
    if not iterations:
        return "Missing iteration specification", 400

    tagnames = body.get("tags")
    if not tagnames:
        return "Missing tagname specification", 400

    names = body.get("name")
    if not names:
        names = ""

    # Convert and get the epc and hdf stream containing the wanted data in RESQML format
    epcstream, hdfstream = convert_ensemble_to_resqml(uuid, iterations, tagnames, names, sumo)

    # Open a stream to contain the zip data
    zipstream = BytesIO()

    # Zip together these two files
    with ZipFile(zipstream, "w") as zip:
        zip.writestr(f"{uuid}.epc", epcstream.getvalue())
        zip.writestr(f"{uuid}.h5", hdfstream.getvalue())

    # Output the zip stream
    return zipstream.getvalue(), 200


@handle_exceptions
@verify_token
def get_ensemble_epc() -> bytes:
    """
        Retrieve an EPC file of all realizations given case ID and iteration number.

        Returns an unzipped EPC file.
    """

    # Initialize and get the sumo exporer
    sumo = get_explorer(request)

    # Retrieve the json data from the request body
    body = request.get_json()

    # Retrieve case id from the request
    uuid = body.get("uuid")
    if not uuid:
        return "Missing object uuid", 400

    # Retrieve filter information from request
    iterations = body.get("iter")
    if not iterations:
        return "Missing iteration specification", 400

    tagnames = body.get("tags")
    if not tagnames:
        return "Missing tagname specification", 400

    names = body.get("name")
    if not names:
        names = ""

    # Convert and get the epc stream containing the wanted data in RESQML format
    epcstream, _ = convert_ensemble_to_resqml(uuid, iterations, tagnames, names, sumo)

    # Output the epc stream
    return epcstream.getvalue(), 200


@handle_exceptions
@verify_token
def get_ensemble_hdf() -> bytes:
    """
        Retrieve an HDF5 file of all realizations given case ID and iteration number.

        Returns an unzipped HDF5 file.
    """
    
    # Initialize and get the sumo exporer
    sumo = get_explorer(request)

    # Retrieve the json data from the request body
    body = request.get_json()

    # Retrieve case id from the request
    uuid = body.get("uuid")
    if not uuid:
        return "Missing object uuid", 400

    # Retrieve filter information from request
    iterations = body.get("iter")
    if not iterations:
        return "Missing iteration specification", 400

    tagnames = body.get("tags")
    if not tagnames:
        return "Missing tagname specification", 400

    names = body.get("name")
    if not names:
        names = ""

    # Convert and get the hdf stream containing the wanted data in RESQML format
    _, hdfstream = convert_ensemble_to_resqml(uuid, iterations, tagnames, names, sumo)

    # Output the hdf stream
    return hdfstream.getvalue(), 200