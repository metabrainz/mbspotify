from __future__ import print_function
from flask_testing import TestCase
from flask import current_app
from mbspotify import create_app
import subprocess
import psycopg2
import json
import os

SQL_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), '..', 'sql')


def _run_psql(app, script, user=None, database=None):
    script = os.path.join(SQL_DIR, script)
    command = ['psql', '-h', app.config["PG_INFO"]["host"],
               '-p', str(app.config["PG_INFO"]["port"]),
               '-U', user or app.config["PG_INFO"]["user"],
               '-d', database or app.config["PG_INFO"]["database"],
               '-f', script]
    exit_code = subprocess.call(command)
    return exit_code


class ViewsTestCase(TestCase):

    def setUp(self):
        self.mbid = "10000000-0000-0000-0000-000000000001"
        self.spotify_uri = "spotify:album:42"
        self.another_spotify_uri = "spotify:album:123"
        self.users = [
            "00000000-0000-0000-0000-000000000001",
            "00000000-0000-0000-0000-000000000002",
            "00000000-0000-0000-0000-000000000003",
            "00000000-0000-0000-0000-000000000004",
            "00000000-0000-0000-0000-000000000005",
            "00000000-0000-0000-0000-000000000006",
        ]
        self.json_headers = {"Content-Type": "application/json"}

        with psycopg2.connect(**self.app.config["PG_INFO"]) as conn:
            with conn.cursor() as cur:
                cur.execute("DROP TABLE IF EXISTS mapping_vote CASCADE;")
                cur.execute("DROP TABLE IF EXISTS mapping      CASCADE;")
                conn.commit()
        _run_psql(current_app, 'create_tables.sql', user='mbspotify', database='mbspotify')

    def tearDown(self):
        pass

    def create_app(self):
        app = create_app(config_path=os.path.join(
            os.path.dirname(os.path.realpath(__file__)),
            'test_config.py'
        ))
        return app

    def test_vote(self):
        # Adding a new mapping
        self.client.post(
            "mapping/add?key=%s" % self.app.config["ACCESS_KEYS"][0],
            headers=self.json_headers,
            data=json.dumps({
                "mbid": self.mbid,
                "spotify_uri": self.spotify_uri,
                "user": self.users[0]})
        )

        # All users are voting against a mapping
        for user in self.users:
            self.client.post(
                "/mapping/vote?key=%s" % self.app.config["ACCESS_KEYS"][0],
                headers=self.json_headers,
                data=json.dumps({
                    "mbid": self.mbid,
                    "spotify_uri": self.spotify_uri,
                    "user": user,
                })
            )

        # Mapping should be deleted now
        response = self.client.post(
            "/mapping",
            headers=self.json_headers,
            data=json.dumps({"mbid": self.mbid})
        )
        self.assertEquals(response.json, {
            "mbid": self.mbid,
            "mappings": [],
        })

        # And we should be able to add the same mapping again
        self.client.post(
            "mapping/add?key=%s" % self.app.config["ACCESS_KEYS"][0],
            headers=self.json_headers,
            data=json.dumps({
                "mbid": self.mbid,
                "spotify_uri": self.spotify_uri,
                "user": self.users[0]})
        )
        response = self.client.post("/mapping", headers=self.json_headers,
                                    data=json.dumps({"mbid": self.mbid}))
        self.assertEquals(response.json, {
            "mbid": self.mbid,
            "mappings": [self.spotify_uri],
        })

        # Let's try voting multiple times as the same user
        for _ in range(10):
            self.client.post(
                "/mapping/vote?key=%s" % self.app.config["ACCESS_KEYS"][0],
                headers=self.json_headers,
                data=json.dumps({
                    "mbid": self.mbid,
                    "spotify_uri": self.spotify_uri,
                    "user": self.users[0],
                })
            )

        # Mapping should still be there
        response = self.client.post("/mapping", headers=self.json_headers,
                                    data=json.dumps({"mbid": self.mbid}))
        self.assertEquals(response.json, {
            "mbid": self.mbid,
            "mappings": [self.spotify_uri],
        })

    def test_mapping(self):
        response = self.client.post(
            "/mapping",
            headers=self.json_headers,
            data=json.dumps({"mbid": self.mbid})
        )
        self.assertEquals(response.json, {
            "mbid": self.mbid,
            "mappings": [],
        })

        # Adding a new mapping
        self.client.post(
            "mapping/add?key=%s" % self.app.config["ACCESS_KEYS"][0],
            headers=self.json_headers,
            data=json.dumps({
                "mbid": self.mbid,
                "spotify_uri": self.spotify_uri,
                "user": self.users[0]
            })
        )

        response = self.client.post("/mapping", headers=self.json_headers,
                                    data=json.dumps({"mbid": self.mbid}))
        self.assertEquals(response.json, {
            "mbid": self.mbid,
            "mappings": [self.spotify_uri],
        })

        # Adding another mapping for the same MBID
        self.client.post(
            "mapping/add?key=%s" % self.app.config["ACCESS_KEYS"][0],
            headers=self.json_headers,
            data=json.dumps({
                "mbid": self.mbid,
                "spotify_uri": self.another_spotify_uri,
                "user": self.users[0]
            })
        )

        response = self.client.post("/mapping", headers=self.json_headers,
                                    data=json.dumps({"mbid": self.mbid}))
        self.assertEquals(response.json, {
            "mbid": self.mbid,
            "mappings": [self.spotify_uri, self.another_spotify_uri],
        })

    def mapping_spotify(self):
        response = self.client.get("/mapping-spotify?spotify_uri=%s" % self.spotify_uri)
        self.assertEquals(response.json, {
            "mappings": [],
        })

        # Adding a new mapping
        self.client.post(
            "mapping/add?key=%s" % self.app.config["ACCESS_KEYS"][0],
            headers=self.json_headers,
            data=json.dumps({
                "mbid": self.mbid,
                "spotify_uri": self.spotify_uri,
                "user": self.users[0]
            })
        )

        response = self.client.get("/mapping-spotify?spotify_uri=%s" % self.spotify_uri)
        self.assertEquals(response.json, {
            "mappings": [
                self.mbid,
            ],
        })

    def test_mapping_jsonp(self):
        response = self.client.get("/mapping-jsonp/%s" % self.mbid)
        self.assertEquals(response.json, {})

        # Adding a new mapping
        self.client.post(
            "mapping/add?key=%s" % self.app.config["ACCESS_KEYS"][0],
            headers=self.json_headers,
            data=json.dumps({
                "mbid": self.mbid,
                "spotify_uri": self.spotify_uri,
                "user": self.users[0],
            })
        )

        response = self.client.get("/mapping-jsonp/%s" % self.mbid)
        self.assertEquals(response.json, {self.mbid: self.spotify_uri})
