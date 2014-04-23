#!/usr/bin/env python

import os
import json
import psycopg2
from flask import Flask, request
import config

app = Flask(__name__)

@app.route('/')
def index():
    return "<html>Piss off!</html>"

@app.route('/mapping/add')
def add():
    return "{}"

@app.route('/mapping', methods=["POST"])
def mapping():
    id_tuple = tuple(request.json['mbids'])
   
    conn = psycopg2.connect(config.PG_CONNECT)
    cur = conn.cursor()

    cur.execute('''SELECT mbid, spotify_uri FROM mapping WHERE mbid in %s''' % (id_tuple,))
    
    data = {}
    for row in cur.fetchall():
        data[row[0]] = row[1]

    return json.dumps({ "mapping" : data})

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=8080)
