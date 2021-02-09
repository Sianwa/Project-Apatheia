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

app = Flask(__name__)
        
        
#Make connection when server loads
con = connection()

@app.route('/')
def hello():
    #render landing page
    return render_template("index.html")

@app.route('/trade', methods=['POST'])
def trade():
    try:
        
        if 'currency_pair' in request.form and 'lot_size' in request.form:
            currency_pair = request.form['currency_pair']
            lotSize = request.form['lot_size']
            render_template("success.html")
            #returns profits generated
            result = SimulateTrade(currency_pair, lotSize, con)
            
            print(result)
        else:
            response = "Invalid Inputs"
        return response

    except Exception as e:
        return render_template("500.html")
       
#test route
@app.route('/test', methods=['GET'])
def test():
   return render_template("success.html")

@app.route('/terminate', methods=['POST'])
def killSwitch():
    try:
        if(con.is_connected()):
            print(con.get_accounts_summary()['balance'])
            con.close()
            return "Connection Closed" 

    except Exception as e:
        return render_template("500.html")

@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"),404

@app.errorhandler(500)
def server_error(e):
    return render_template("500.html"),500



if __name__ == '__main__':
    app.run(debug = True)