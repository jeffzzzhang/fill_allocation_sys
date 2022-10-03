
import os
import json
import time
import random
import logging
import threading
from threading import Thread
from datetime import datetime as dt
import flask
import pymongo
from flask import Flask,request,render_template,send_from_directory, redirect,url_for

app = Flask(__name__)

@app.route("/test", methods=["GET", "POST"])
def test():
    if flask.request.method == 'POST':
        results = flask.request.json
        print(json.loads(results))
        logging.info(f"""json.loads(results)""")
        return results

if __name__ == '__main__':
    """
    launch position server by running this script
    """
    app.run(host="0.0.0.0", port=9998, debug=True, threaded=True)
 