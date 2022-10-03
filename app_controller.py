
import os
import json
import time
import random
import logging
import threading
from threading import Thread
from datetime import datetime as dt
import flask
import redis
import pymongo
from flask import Flask,request,render_template,send_from_directory, redirect,url_for
from constants import constants as cnst

app = Flask(__name__)

@app.route("/ctrl", methods=["GET", "POST"])
def test():
    if flask.request.method == 'POST':
        '''
        position = 'position' in flask.request.form and flask.request.form['position'] # 
        value = 'value' in flask.request.form and flask.request.form['value'] 
        print('position: ', position,', and value: ', value)
        logging.info(f"""CONTROLLER: request info received - {flask.request.form.to_dict()}, 
                      and type is {type(flask.request.form.to_dict())}, dir includes {dir(flask.request.form)}""")
        '''
        tmp = flask.request.form.to_dict()
        print(tmp)
        redis_pool = redis.ConnectionPool(host=cnst.queue_ip, port=cnst.queue_port)
        with redis.Redis(connection_pool=redis_pool) as conn:
            conn.lpush('queue', json.dumps(tmp))
        logging.info('Posted content is pushed to mq')
    return 'Message received'
 

if __name__ == '__main__':
    format = "%(asctime)s: %(message)s"
    logging.basicConfig(format=format, level=logging.INFO) #, datefmt="%H:%M:%S.%f"
    app.run(host="0.0.0.0", port=9999, debug=True, threaded=True)
 