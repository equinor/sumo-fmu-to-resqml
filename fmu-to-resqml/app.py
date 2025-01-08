from api.functionality import (
    get_ensemble,
    get_ensemble_epc,
    get_ensemble_hdf,
    get_epc,
    get_hdf,
    get_resqml,
)
from flask import Flask
from flask_cors import CORS

# Create the application
app = Flask(__name__)

# Enable CORS for all routes
CORS(app)

# Route endpoints to functions
app.add_url_rule(
    "/objects/",
    methods=["GET", "POST"],
    endpoint="resqml-retrieval",
    view_func=get_resqml,
)
app.add_url_rule(
    "/objects/epc",
    methods=["GET", "POST"],
    endpoint="epc-retrieval",
    view_func=get_epc,
)
app.add_url_rule(
    "/objects/hdf",
    methods=["GET", "POST"],
    endpoint="hdf-retrieval",
    view_func=get_hdf,
)

app.add_url_rule(
    "/ensemble/",
    methods=["POST"],
    endpoint="ensemble-retrieval",
    view_func=get_ensemble,
)
app.add_url_rule(
    "/ensemble/epc",
    methods=["POST"],
    endpoint="ensemble-epc-retrieval",
    view_func=get_ensemble_epc,
)
app.add_url_rule(
    "/ensemble/hdf",
    methods=["POST"],
    endpoint="ensemble-hdf-retrieval",
    view_func=get_ensemble_hdf,
)


@app.get("/")
def hello_world():
    return "<p> Hello world! </p>"
