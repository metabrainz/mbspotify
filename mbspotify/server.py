#!/usr/bin/env python

import os
import json
import psycopg2
import uuid
from flask import Flask, request, Response
from werkzeug.exceptions import BadRequest, ServiceUnavailable
import config

app = Flask(__name__)

@app.route('/')
def index():
    return "<html>Piss off!</html>"

@app.route('/mapping/add', methods=["POST"])
def add():
    user = request.json['user']
    try:
        val = uuid.UUID(user, version=4)
    except ValueError:
        raise BadRequest

    mbid = request.json['mbid']
    try:
        val = uuid.UUID(mbid, version=4)
    except ValueError:
        raise BadRequest

    uri = request.json['spotify_uri']
    if not uri.startswith("spotify:album:"):
        raise BadRequest

    conn = psycopg2.connect(config.PG_CONNECT)
    cur = conn.cursor()

    try:
        cur.execute('''INSERT INTO mapping (mbid, spotify_uri, cb_user) values (%s, %s, %s)''',
                    (mbid, uri, user))
        conn.commit()
    except psycopg2.IntegrityError, e:
        raise BadRequest(str(e))
    except psycopg2.OperationalError, e:
        raise ServiceUnavailable(str(e))

    response = Response()
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

@app.route('/mapping/vote', methods=["POST"])
def vote():
    user = request.json['user']
    try:
        val = uuid.UUID(user, version=4)
    except ValueError:
        raise BadRequest

    mbid = request.json['mbid']
    try:
        val = uuid.UUID(mbid, version=4)
    except ValueError:
        raise BadRequest

    conn = psycopg2.connect(config.PG_CONNECT)
    cur = conn.cursor()

    try:
        cur.execute('''SELECT id FROM mapping WHERE mbid = %s''', (mbid,))
        if not cur.rowcount:
            raise BadRequest
        row = cur.fetchone()

        cur.execute('''INSERT INTO mapping_vote (mapping, cb_user) VALUES (%s, %s)''', (row[0], user))
        conn.commit()

    except psycopg2.IntegrityError, e:
        raise BadRequest(str(e))
    except psycopg2.OperationalError, e:
        raise ServiceUnavailable(str(e))

    response = Response()
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

@app.route('/mapping', methods=["POST"])
def mapping():
    id_tuple = tuple(request.json['mbids'])
   
    conn = psycopg2.connect(config.PG_CONNECT)
    cur = conn.cursor()

    cur.execute('''SELECT mbid, spotify_uri FROM mapping WHERE mbid in %s''', (id_tuple,))
    
    data = {}
    for row in cur.fetchall():
        data[row[0]] = row[1]

    response = Response(json.dumps({ "mapping" : data}), mimetype="application/json")
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=8080)
