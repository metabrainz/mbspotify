from __future__ import print_function
from flask.ext.testing import TestCase
from server import app
import psycopg2
import json


class ServerTestCase(TestCase):

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

    def tearDown(self):
        conn = psycopg2.connect(self.app.config["PG_CONNECT"])
        cur = conn.cursor()
        cur.execute("TRUNCATE mapping_vote CASCADE;")
        cur.execute("TRUNCATE mapping CASCADE;")
        conn.commit()
        cur.close()
        conn.close()

    def create_app(self):
        app.config["TESTING"] = True
        return app

    def test_index(self):
        response = self.client.get("/")
        # Index page should ask users to piss off.
        assert "Piss off!" in response.data

    def test_add(self):
        # TODO: Implement
        pass

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

        # Let"s try voting multiple times as the same user
        for n in xrange(10):
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
