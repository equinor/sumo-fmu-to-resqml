from flask import Flask

app = Flask(__name__)

@app.get("/")
def hello_world():
    return "<p> Hello world! </p>"

if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1")