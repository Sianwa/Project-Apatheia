import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3' 
import tensorflow as tf
import keras
from keras.models import load_model
import yaml
import numpy as np
from flask import Flask, request, jsonify, render_template, flash
import fxcmpy
import datetime as dt
import socketio
import json
import time
from LiveBot import SimulateTrade
from fxcmConnect import connection
from rq import Queue
import redis
import time
from test import background_task

app = Flask(__name__)
        
        
#connections
#r = redis.Redis()
#q = Queue(connection=r)
con = connection()

#----------------------------------------------------------------------------
@app.route('/')
def hello():
    #render landing page
    return render_template("index.html")

#---------------------------------------------------------------------------
@app.route('/trade', methods=['POST'])
def trade():
    try:
        
        if 'currency_pair' in request.form and 'lot_size' in request.form:
            currency_pair = request.form['currency_pair']
            lotSize = request.form['lot_size']
            render_template("success.html")
            #run in the background to avoid blocking main thread
            result = SimulateTrade(currency_pair, lotSize, con)
            print(result)
        else:
            response = "Invalid Inputs"
        return response

    except Exception as e:
        return render_template("500.html")
#------------------------------------------------------------------------------       
#test route
@app.route('/test')
def test():
    n = 100
    job = q.enqueue(background_task, n)
    q_len = len(q)
    return f"Task ({job.id}) added to queue at {job.enqueued_at}. {q_len} tasks"

#-----------------------------------------------------------------------------
@app.route('/terminate', methods=['POST'])
def killSwitch():
    try:
        if(con.is_connected()):
            print("Connection Closed")
            con.close()
            return render_template("closed.html")

    except Exception as e:
        return render_template("500.html")
#-------------------------------------------------------------------------------
@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"),404

@app.errorhandler(500)
def server_error(e):
    return render_template("500.html"),500
#-------------------------------------------------------------------------------


if __name__ == '__main__':
    app.run(debug = True)