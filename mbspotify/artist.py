#!/usr/bin/env python

import sys
import urllib
import json
import psycopg2
import config, api_call

VARIOUS_ARTISTS_URI = "spotify:artist:deadbeefisreallynomnom"
VARIOUS_ARTISTS_ID = 0

def fetch_artist_json(artist_uri):
    if artist_uri == VARIOUS_ARTISTS_URI:
        return None
    return api_call.api_call("http://ws.spotify.com/lookup/1/?uri=%s" % urllib.quote_plus(artist_uri))

def get_or_insert_artist(conn, artist_uri):

    if artist_uri == VARIOUS_ARTISTS_URI:
        return VARIOUS_ARTISTS_ID

    print "Get or insert artist: '%s'" % artist_uri
    cur = conn.cursor()
    cur.execute('''SELECT id FROM artist WHERE artist_uri = %s''', (artist_uri,))
    row = cur.fetchone()
    if not row:
        data, e = fetch_artist_json(artist_uri)
        if data:
            print json.dumps(data, sort_keys=True, indent=4);
            cur.execute('''INSERT INTO artist (id, artist_uri, name, json) 
                                VALUES (DEFAULT, %s, %s, %s) 
                             RETURNING id''', (artist_uri, data[0]['artist']['name'], json.dumps(data)))
            row = cur.fetchone()
            return row[0]
        else:
            return None
    else:
        return row[0]
