#!/usr/bin/env python
import json
import psycopg2
import logging
import config
from utils import validate_uuid
from decorators import key_required
from logging.handlers import RotatingFileHandler
from flask import Flask, request, Response
from flask.ext.jsonpify import jsonify
from werkzeug.exceptions import BadRequest, ServiceUnavailable

app = Flask(__name__)

# Configuration
app.config.from_object(config)

# Error handling and logging
handler = RotatingFileHandler("/tmp/mbspotify.log")
handler.setLevel(logging.WARNING)
app.logger.addHandler(handler)


@app.route('/')
def index():
    return "<html>Piss off!</html>"


@app.route("/mapping/add", methods=["POST"])
@key_required
def add():
    """Endpoint for adding new mappings to Spotify.

    Only connection to albums on Spotify is supported right now.

    JSON parameters:
        user: UUID of the user who is adding new mapping.
        mbid: MusicBrainz ID of an entity that is being connected.
        spotify_uri: Spotify URI of an album that is being connected.
    """
    user = request.json["user"]
    if not validate_uuid(user):
        raise BadRequest("Incorrect user ID (UUID).")

    mbid = request.json["mbid"]
    if not validate_uuid(mbid):
        raise BadRequest("Incorrect MBID (UUID).")

    uri = request.json["spotify_uri"]
    if not uri.startswith("spotify:album:"):
        raise BadRequest("Incorrect Spotify URI. Only albums are supported right now.")

    conn = psycopg2.connect(config.PG_CONNECT)
    cur = conn.cursor()

    try:
        # Checking if mapping is already created
        cur.execute("SELECT id FROM mapping "
                    "WHERE is_deleted = FALSE "
                    "AND mbid = %s "
                    "AND spotify_uri = %s", (mbid, uri))
        if not cur.rowcount:
            # and if it's not, adding it
            cur.execute("INSERT INTO mapping (mbid, spotify_uri, cb_user, is_deleted)"
                        "VALUES (%s, %s, %s, FALSE)",
                        (mbid, uri, user))
            conn.commit()
    except psycopg2.IntegrityError, e:
        raise BadRequest(str(e))
    except psycopg2.OperationalError, e:
        raise ServiceUnavailable(str(e))

    response = Response()
    response.headers["Access-Control-Allow-Origin"] = "*"
    return response


@app.route('/mapping/vote', methods=["POST"])
@key_required
def vote():
    user = request.json["user"]
    if not validate_uuid(user):
        raise BadRequest("Incorrect user ID (UUID).")

    mbid = request.json["mbid"]
    if not validate_uuid(mbid):
        raise BadRequest("Incorrect MBID (UUID).")

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

    # Check if threshold is reached. And if it is, marking mapping as deleted.
    try:
        cur.execute('''SELECT *
                       FROM mapping_vote
                       JOIN mapping ON mapping_vote.mapping = mapping.id
                       WHERE mapping.mbid = %s''', (mbid,))
        if cur.rowcount >= app.config['THRESHOLD']:
            cur.execute('''UPDATE mapping SET is_deleted = TRUE WHERE mbid = %s''', (mbid,))
            conn.commit()

    except psycopg2.IntegrityError, e:
        raise BadRequest(str(e))
    except psycopg2.OperationalError, e:
        raise ServiceUnavailable(str(e))

    response = Response()
    response.headers['Access-Control-Allow-Origin'] = '*'
    return response


@app.route('/mapping', methods=["POST"])
def mapping():
    id_tuple = tuple(request.json['mbids'])
   
    conn = psycopg2.connect(config.PG_CONNECT)
    cur = conn.cursor()

    cur.execute('''SELECT mbid, spotify_uri FROM mapping WHERE is_deleted = FALSE AND mbid in %s''', (id_tuple,))
    
    data = {}
    for row in cur.fetchall():
        data[row[0]] = row[1]

    response = Response(json.dumps({"mapping": data}), mimetype="application/json")
    response.headers['Access-Control-Allow-Origin'] = '*'
    return response


@app.route('/mapping-jsonp/<mbid>')
def mapping_jsonp(mbid):
    conn = psycopg2.connect(config.PG_CONNECT)
    cur = conn.cursor()

    cur.execute('''SELECT mbid, spotify_uri FROM mapping WHERE is_deleted = FALSE AND mbid = %s''', (mbid,))
    if not cur.rowcount:
        return jsonify({})
    row = cur.fetchone()
    return jsonify({mbid: row[1]})


if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=8080)
