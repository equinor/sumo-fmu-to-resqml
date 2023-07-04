from flask import Flask

from functionality import *


# Create the application
app = Flask(__name__)


# Route endpoints to functions
app.add_url_rule("/objects/", methods=["GET", "POST"], endpoint="resqml-retrieval", view_func=get_resqml)
app.add_url_rule("/objects/epc", methods=["GET", "POST"], endpoint="epc-retrieval", view_func=get_epc)
app.add_url_rule("/objects/hdf", methods=["GET", "POST"], endpoint="hdf-retrieval", view_func=get_hdf)


@app.get("/")
def hello_world():
    return "<p> Hello world! </p>"