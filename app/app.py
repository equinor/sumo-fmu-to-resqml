from flask import Flask, send_file, request

from encoding import json_to_resqml, write_dict_to_zip_file
from zipfile import ZipFile, ZIP_DEFLATED
from io import BytesIO
import os

from fmu.sumo.explorer import Explorer

# Run application
app = Flask(__name__)
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")


@app.get("/")
def hello_world():
    return "<p> Hello world! </p>"



@app.get("/objects/alt")
def get_objects_alternative():
    """
        Retrieve all unfiltered metadata for a given object.
    """
    token = request.headers.get("Authorization")
    if not token:
        return "Missing authorization token in header", 401
    
    token = token.split(" ")[1]
    sumo = Explorer("dev", token)

    uuid = request.args.get("id")
    if not uuid:
        return "Missing object id", 400

    try:
        metadata = sumo._utils.get_object(uuid)
    except Exception as e:
        return f"{e} while searching for object:'{uuid}'.\n\nUse POST for retrieving several objects", 404
    
    return json_to_resqml(metadata)


@app.post("/objects/alt")
def get_several_objects_alternative():
    """
        Retrieve all unfiltered metadata for several given objects.
    """
    token = request.headers.get("Authorization")
    if not token:
        return "Missing authorization token in header", 401
    
    token = token.split(" ")[1]
    sumo = Explorer("dev", token)

    ids = request.form.get("ids")
    if not ids:
        return "Missing object ids", 400

    zipstream = BytesIO()
    with ZipFile(zipstream, "w") as zip:
        for uuid in ids.split(";"):
            try:
                metadata = sumo._utils.get_object(uuid)
            except Exception as e:
                return f"'{e}' while searching for object:'{uuid}'.", 404
        
            write_dict_to_zip_file(metadata, zip, uuid+".resqml")

    output = zipstream.getvalue()
    zipstream.close()

    return output


@app.get("/objects/")
def get_objects_as_resqml():
    """
        Retrieve metadata of a given object.
    """
    token = request.headers.get("Authorization")
    if not token:
        return "Missing authorization token in header", 401
    
    token = token.split(" ")[1]
    sumo = Explorer("dev", token)

    uuid = request.args.get("id")
    if not uuid:
        return "Missing object id", 400
    
    object_type = request.args.get("object_type")
    if not object_type:
        return "Missing object type", 400

    #### Explorer.py implements sumo._utils.get_object(uuid) which gets all metadata directly (regardless of type)
    match object_type:
        case "surface":
            object = sumo.get_surface_by_uuid(uuid)
        case "polygon":
            object = sumo.get_polygons_by_uuid(uuid)
        case "table":
            object = sumo.get_table_by_uuid(uuid)
        case _:
            return f"{object_type} not recognized. Valid object types are ['surface', 'polygon', 'table']"
    
    if not object:
        return f"Object:'{uuid}' not found", 404
    
    return json_to_resqml(object.metadata)


@app.post("/objects/")
def get_several_objects_as_resqml():
    """
        Retrieve metadata of several objects as resqml.
    """
    token = request.headers.get("Authorization")
    if not token:
        return "Missing authorization token in header", 401
    
    token = token.split(" ")[1]
    sumo = Explorer("dev", token)

    ids_types = request.form.get("ids")
    if not ids_types:
        return "Missing object ids and object types", 400

    zipstream = BytesIO()
    with ZipFile(zipstream, "w") as zip:

        for id_type in ids_types.split(";"):
            uuid, object_type = id_type.split(",")
            #### Explorer.py implements sumo._utils.get_object(uuid) which gets all metadata directly (regardless of type)
            match object_type:
                case "surface":
                    object = sumo.get_surface_by_uuid(uuid)
                case "polygon":
                    object = sumo.get_polygons_by_uuid(uuid)
                case "table":
                    object = sumo.get_table_by_uuid(uuid)
                case _:
                    return f"{object_type} not recognized. Valid object types are ['surface', 'polygon', 'table']"

            if not object:
                return f"Object:'{uuid}' not found", 404
        
            write_dict_to_zip_file(object.metadata, zip, uuid+".resqml")

    output = zipstream.getvalue()
    zipstream.close()

    return output


# Retrieve sample case
@app.get("/sample-resqml/")
def sample_resqml():
    token = request.headers.get("Authorization")
    if not token:
        return "Missing authorization token in header", 401
    
    token = token.split(" ")[1]
    
    sumo = Explorer("dev", token)

    polygon = sumo.cases.filter(asset="Drogon")[1].polygons[0]
    return json_to_resqml(polygon.metadata)