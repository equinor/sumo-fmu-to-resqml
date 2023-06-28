from flask import Flask

from functionality import *



# Run application
app = Flask(__name__)
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")


@app.get("/")
def hello_world():
    return "<p> Hello world! </p>"


app.add_url_rule("/objects/", methods = ["GET"], view_func=get_objects)
app.add_url_rule("/objects/hdf", methods = ["GET"], view_func=get_objects_hdf)

app.add_url_rule("/objects/", methods = ["POST"], view_func=get_several_objects)
