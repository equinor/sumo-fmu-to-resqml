from flask import Flask

from deprecated.functionality import *



# Create the application
app = Flask(__name__)


# Route endpoints to functions
app.add_url_rule("/objects/", methods = ["GET"], view_func=get_objects)
app.add_url_rule("/objects/data", methods = ["GET"], view_func=get_objects_hdf)

app.add_url_rule("/objects/", methods = ["POST"], view_func=get_several_objects)
app.add_url_rule("/objects/data", methods = ["POST"], view_func=get_several_objects_hdf)

@app.get("/")
def hello_world():
    return "<p> Hello world! </p>"