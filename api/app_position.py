import json
import logging
import flask
from flask import Flask

app = Flask(__name__)


@app.route("/test", methods=["GET", "POST"])
def test():
    if flask.request.method == "POST":
        results = flask.request.json
        print(json.loads(results))
        logging.info(f"""json.loads(results)""")
        return results

if __name__ == "__main__":
    """
    launch position server by running this script
    """
    app.run(host="0.0.0.0", port=9998, debug=True, threaded=True)
