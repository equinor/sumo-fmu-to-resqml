from flask import Flask

from _deprecated._functionality import *
from functionality import *


# Create the application
app = Flask(__name__)


# Route endpoints to functions (Deprecated)
app.add_url_rule("/depr/objects/", methods=["GET"], view_func=get_objects)
app.add_url_rule("/depr/objects/data", methods=["GET"], view_func=get_objects_hdf)

app.add_url_rule("/depr/objects/", methods=["POST"], view_func=get_several_objects)
app.add_url_rule("/depr/objects/data", methods=["POST"], view_func=get_several_objects_hdf)

# (Not deprecated)
app.add_url_rule("/objects/", methods=["GET", "POST"], endpoint="resqml-retrieval", view_func=get_resqml)
app.add_url_rule("/objects/epc", methods=["GET", "POST"], endpoint="epc-retrieval", view_func=get_epc)
app.add_url_rule("/objects/hdf", methods=["GET", "POST"], endpoint="hdf-retrieval", view_func=get_hdf)

@app.get("/")
def hello_world():
    return "<p> Hello world! </p>"