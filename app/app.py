from flask import Flask

from _deprecated._functionality import *
from functionality import *


# Create the application
app = Flask(__name__)


# Route endpoints to functions (Deprecated)
app.add_url_rule("v1/objects/", methods=["GET"], view_func=get_objects)
app.add_url_rule("v1/objects/data", methods=["GET"], view_func=get_objects_hdf)

app.add_url_rule("v1/objects/", methods=["POST"], view_func=get_several_objects)
app.add_url_rule("v1/objects/data", methods=["POST"], view_func=get_several_objects_hdf)

# (Not deprecated)
app.add_url_rule("/objects/", methods=["GET", "POST"], endpoint="resqml-retrieval", view_func=get_resqml)

@app.get("/")
def hello_world():
    return "<p> Hello world! </p>"