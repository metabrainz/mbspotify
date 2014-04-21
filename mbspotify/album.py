import sys
import psycopg2
import json
from time import sleep
import artist, config, countries, api_call

def fetch_album_json(album_uri):
    return api_call.api_call("http://ws.spotify.com/lookup/1/?uri=%s" % album_uri)

def insert_album(conn, name, data):
    """ Caller must have transaction open and catch errors! """

    artist_id = artist.get_or_insert_artist(conn, data["album"]["artist-id"])
    if not artist_id:
        return

    cur = conn.cursor()
    sql = '''INSERT INTO album (album_uri, artist, name, json) 
                  VALUES (%s, %s, %s, %s) RETURNING id''';

    cur.execute(sql, (data["album"]["href"], artist_id, name, json.dumps(data)))
    row = cur.fetchone()
    album_id = row[0]
    countries.insert_country_string(cur, album_id, data['album']['availability']['territories'])

def album_exists(conn, album_uri):
    cur = conn.cursor()
    cur.execute('''SELECT id FROM album WHERE album_uri = %s''', (album_uri,))
    row = cur.fetchone()
    if not row: return None
    return row[0] 
