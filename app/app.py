from flask import Flask, render_template

# Standard library
import os
import sys
import re
from functools import wraps

# Third-party
from flask import (
    Flask,
    request,
    redirect,
    url_for,
    render_template,
    session,
    jsonify,
    make_response,
    abort,
)

from datetime import datetime, timezone

from flask import render_template, redirect, url_for, request, abort



import stripe
from flask import jsonify, request, session, redirect, url_for
from datetime import datetime
import random, os
import pillow_heif






import os
base_dir = os.getcwd()+'/'









#################################################################################################
#-Child level - DB setup (Feb 25 - V1)
#################################################################################################

import os

def run_file(filename):
    d = os.getcwd()
    f = None

    while not f:
        for r, _, files in os.walk(d):
            if filename in files:
                f = os.path.join(r, filename)
                break
        if f or os.path.dirname(d) == d:
            break
        d = os.path.dirname(d)

    if not f:
        raise FileNotFoundError(f"{filename} not found")

    exec(open(f).read(), globals())



try:
    master_dir
except NameError:
    master_dir = False



#Child Dir System Setup -- Use for Testing
if not master_dir:
    run_file("mysqlconnector.py")
    run_file("selenium_setup.py")


    
    #Define the Db you are using
    print('')
    run_sql('use new_algo_db ')
    print('')

    
    #get a test_ticker_list to test in your script
    #probs hardcode this actually so it dosent break
    #job for another day
    ###########################################################
    df = run_sql("""
    select * from scraper__wsj_gainers;
    """).to_df()
    test_ticker_list = df['ticker'].to_list()
    test_ticker_list = list(set(test_ticker_list))[:30]
    ###########################################################



    
    print('Child level system setup success ')
    print("\nNOTE: use test_ticker_list to test function")

    

#################################################################################################





run_sql("""

show databases;
use new_algo_db;


""")





#GLOBAL VARIABLES
################################################################

STRIPE_BACK_END_KEY = os.environ.get("STRIPE_BACK_END_KEY", "")
STRIPE_FRONT_END_KEY = os.environ.get("STRIPE_FRONT_END_KEY", "")

################################################################









#app = Flask(__name__)
app = Flask(__name__, static_folder='static')  # ✅ This is still fine
app.config['SECRET_KEY'] = os.environ.get("FLASK_SECRET_KEY", "dev-only-secret-key")  # required for sessions


import os

if not globals().get("_ENDPOINTS_LOADED"):
    _ENDPOINTS_LOADED = True

    endpoint_files = []

    python_files = os.listdir(base_dir + "/endpoints")

    Y = 0
    while Y < len(python_files):

        if python_files[Y].endswith(".py"):
            endpoint_files.append(python_files[Y])

        Y += 1

    endpoint_files.sort()

    for file in endpoint_files:
        path = os.path.join(base_dir, "endpoints", file)
        with open(path, "r") as f:
            exec(f.read(), globals())













if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5009, debug=True)

