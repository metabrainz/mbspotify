#!/usr/bin/env python

import sys
import psycopg2
from time import sleep
import album, config

def add_album(album_uri):
    try:
        conn = psycopg2.connect(config.PG_CONNECT)
    except psycopg2.OperationalError as err:
        return "Cannot connect to database: %s" % err

    if album.album_exists(conn, album_uri):
        return "This album already exists"

    data, err = album.fetch_album_json(album_uri)
    if not data: return err

    album.insert_album(conn, album_uri, data['data)
    try:
        conn.commit()
    except psycopg2.IntegrityError, e:
        conn.rollback()
        return "Commit failed: %s" % e

    return ""

if len(sys.argv) == 1:
    while True:
        line = sys.stdin.readline()
        if not line: break
        album_uri = line[:-1]
        e = add_album(album_uri)
        if e: 
            print e
        else:
            print "added: %s" % album_uri
        sleep(.12)
else:
    album_uri = sys.argv[1] 
    e = add_album(album_uri)
    if e: 
        print e
    else:
        print "album added: %s" % album_uri
