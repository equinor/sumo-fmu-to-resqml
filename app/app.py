from flask import Flask, send_file, request

from encoding import json_to_resqml

from fmu.sumo.explorer import Explorer

# Run application
app = Flask(__name__)
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")


@app.get("/")
def hello_world():
    return "<p> Hello world! </p>"


@app.get("/object/")
def get_object_as_resqml():
    """
        Retrieve metadata of a given object
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
        return "Object not found", 400
    
    return json_to_resqml(object.metadata)


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