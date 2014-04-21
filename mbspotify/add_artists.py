#!/usr/bin/env python

import sys
import urllib
import json;
from time import sleep
import psycopg2
import config, artist, api_call

def search_artist(artist):
    return api_call.api_call("http://ws.spotify.com/search/1/artist.json?q=%s" % 
                             urllib.quote_plus(artist))

try:
    conn = psycopg2.connect(config.PG_CONNECT)
    cur = conn.cursor()
except psycopg2.OperationalError as err:
    print "Cannot connect to database: %s" % err
    exit()

while True:
    line = sys.stdin.readline()
    if not line: break
    name = line.strip()
    data, err = search_artist(name)
    if err: 
        print "search artist %s failed: %s" % (name, err)
    else:
        try:
            artist_uri = data['artists'][0]['href']
        except KeyError:
            print "Cannot find artist-id in returned data."
            continue

        id = artist.get_or_insert_artist(conn, artist_uri)
        print "%s -> %d" % (artist_uri, id)
        conn.commit()
            
    sleep(.1)
