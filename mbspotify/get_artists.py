#!/usr/bin/env python

import sys
import urllib
import json;
from time import sleep
import psycopg2
import config, artist, api_call

def fetch_album_json(album_uri):
    return api_call.api_call("http://ws.spotify.com/lookup/1/?uri=%s" % 
                             urllib.quote_plus(album_uri))
try:
    conn = psycopg2.connect(config.PG_CONNECT)
    cur = conn.cursor()
except psycopg2.OperationalError as err:
    print "Cannot connect to database: %s" % err
    exit()

while True:
    line = sys.stdin.readline()
    if not line: break
    uri = line.strip()
    data, err = fetch_album_json(uri)
    if err: 
        print "fetch album %s failed: %s" % (uri, err)
    else:
        try:
            artist_uri = data['album']['artist-id']
        except KeyError:
            if data['album']['artist'] != "Various Artists":
                print "Cannot find artist-id in returned data."
            continue

        id = artist.get_or_insert_artist(conn, artist_uri)
        print "%s -> %d" % (artist_uri, id)
            
    sleep(.1)
