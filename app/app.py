from flask import Flask, send_file

from encoding import json_to_resqml

from fmu.sumo.explorer import Explorer
sumo = Explorer("dev")

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
    polygon = sumo.cases.filter(asset="Drogon")[1].polygons[0]
    return f"<textarea style='width:90vw;height:90vh;border:none;'>{json_to_resqml(polygon.metadata)}</textarea>"