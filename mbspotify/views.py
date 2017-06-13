#!/usr/bin/env python
from flask import Blueprint, request, Response, jsonify, current_app
from werkzeug.exceptions import BadRequest, ServiceUnavailable
from mbspotify.decorators import key_required, jsonp
from mbspotify.utils import validate_uuid
import psycopg2
import json


main_bp = Blueprint('ws_review', __name__)


@main_bp.route("/")
def index():
    return (
        '<html>'
            '<head>'
                '<title>Redirecting to our Github page...</title>
                '<meta http-equiv="refresh" content="1; url=https://github.com/metabrainz/mbspotify" />'
                '<script type="text/javascript">'
                    'window.location.href = "http://example.com"'
                '</script>'
            '</head>'
            '<body>'
                'If you are not automatically redirected, please click ' 
                '<a href="https://github.com/metabrainz/mbspotify">here</a>.'
            '</body>'
        '</html>'
    )


@main_bp.route("/mapping/add", methods=["POST"])
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

    conn = psycopg2.connect(**current_app.config["PG_INFO"])
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
    except psycopg2.IntegrityError as e:
        raise BadRequest(str(e))
    except psycopg2.OperationalError as e:
        raise ServiceUnavailable(str(e))

    response = Response()
    response.headers["Access-Control-Allow-Origin"] = "*"
    return response


@main_bp.route("/mapping/vote", methods=["POST"])
@key_required
def vote():
    """Endpoint for voting against incorrect mappings.

    JSON parameters:
        user: UUID of the user who is voting.
        mbid: MusicBrainz ID of an entity that has incorrect mapping.
        spotify_uri: Spotify URI of an incorrectly mapped entity.
    """
    user = request.json["user"]
    if not validate_uuid(user):
        raise BadRequest("Incorrect user ID (UUID).")

    mbid = request.json["mbid"]
    if not validate_uuid(mbid):
        raise BadRequest("Incorrect MBID (UUID).")

    spotify_uri = request.json["spotify_uri"]

    conn = psycopg2.connect(**current_app.config["PG_INFO"])
    cur = conn.cursor()

    try:
        cur.execute("SELECT id FROM mapping WHERE mbid = %s AND spotify_uri = %s",
                    (mbid, spotify_uri))
        if not cur.rowcount:
            raise BadRequest("Can't find mapping between specified MBID and Spotify URI.")
        mapping_id = cur.fetchone()[0]

        # Checking if user have already voted
        cur.execute("SELECT id FROM mapping_vote WHERE mapping = %s AND cb_user = %s",
                    (mapping_id, user))
        if cur.rowcount:
            raise BadRequest("You already voted against this mapping.")

        cur.execute("INSERT INTO mapping_vote (mapping, cb_user) VALUES (%s, %s)",
                    (mapping_id, user))
        conn.commit()

    except psycopg2.IntegrityError as e:
        raise BadRequest(str(e))
    except psycopg2.OperationalError as e:
        raise ServiceUnavailable(str(e))

    # Check if threshold is reached. And if it is, marking mapping as deleted.
    try:
        cur.execute("SELECT * "
                    "FROM mapping_vote "
                    "JOIN mapping ON mapping_vote.mapping = mapping.id "
                    "WHERE mapping.mbid = %s"
                    "      AND mapping.spotify_uri = %s"
                    "      AND mapping.is_deleted = FALSE",
                    (mbid, spotify_uri))
        if cur.rowcount >= current_app.config["THRESHOLD"]:
            cur.execute("UPDATE mapping SET is_deleted = TRUE "
                        "WHERE mbid = %s AND spotify_uri = %s",
                        (mbid, spotify_uri))
            conn.commit()

    except psycopg2.IntegrityError as e:
        raise BadRequest(str(e))
    except psycopg2.OperationalError as e:
        raise ServiceUnavailable(str(e))

    response = Response()
    response.headers["Access-Control-Allow-Origin"] = "*"
    return response


@main_bp.route("/mapping", methods=["POST"])
def mapping():
    """Endpoint for getting mappings for a MusicBrainz entity.

    JSON parameters:
        mbid: MBID of the entity that you need to find a mapping for.

    Returns:
        List with mappings to a specified MBID.
    """
    mbid = request.json["mbid"]
    if not validate_uuid(mbid):
        raise BadRequest("Incorrect MBID (UUID).")

    conn = psycopg2.connect(**current_app.config["PG_INFO"])
    cur = conn.cursor()

    cur.execute("SELECT spotify_uri "
                "FROM mapping "
                "WHERE is_deleted = FALSE AND mbid = %s",
                (mbid,))

    response = Response(
        json.dumps({
            "mbid": mbid,
            "mappings": [row[0] for row in cur.fetchall()],
        }),
        mimetype="application/json"
    )
    response.headers["Access-Control-Allow-Origin"] = "*"
    return response


@main_bp.route("/mapping-spotify")
def mapping_spotify():
    """Endpoint for getting MusicBrainz entities mapped to a Spotify URI."""
    uri = request.args.get("spotify_uri")
    if uri is None:
        raise BadRequest("`spotify_uri` argument is missing.")
    if not uri.startswith("spotify:album:"):
        raise BadRequest("Incorrect Spotify URI. Only albums are supported right now.")

    conn = psycopg2.connect(**current_app.config["PG_INFO"])
    cur = conn.cursor()

    cur.execute("""
        SELECT mbid::text
          FROM mapping
         WHERE is_deleted = FALSE AND spotify_uri = %s
    """, (uri,))

    return jsonify({
        "mappings": [row[0] for row in cur.fetchall()],
    })


@main_bp.route("/mapping-jsonp/<mbid>")
@jsonp
def mapping_jsonp(mbid):
    if not validate_uuid(mbid):
        raise BadRequest("Incorrect MBID (UUID).")

    conn = psycopg2.connect(**current_app.config["PG_INFO"])
    cur = conn.cursor()

    cur.execute("SELECT mbid, spotify_uri "
                "FROM mapping "
                "WHERE is_deleted = FALSE AND mbid = %s",
                (mbid,))
    if not cur.rowcount:
        return jsonify({})
    # TODO: Return all mappings to a specified MBID (don't forget to update userscript).
    row = cur.fetchone()
    return jsonify({mbid: row[1]})
