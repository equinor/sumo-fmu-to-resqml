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

# Retrieve sample case
@app.get("/sample-resqml")
def sample_resqml():
    token = request.headers.get("Authorization")
    if not token:
        return "Missing authorization token", 401
    
    token = token.split(" ")[1]
    
    sumo = Explorer("dev", token)

    polygon = sumo.cases.filter(asset="Drogon")[1].polygons[0]
    return json_to_resqml(polygon.metadata)