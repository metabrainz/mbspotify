from __future__ import print_function
from flask.ext.testing import TestCase
from server import app
import json


class ServerTest(TestCase):

    def create_app(self):
        app.config['TESTING'] = True
        return app

    def test_index(self):
        response = self.client.get("/")
        # Index page should ask users to piss off.
        assert "Piss off!" in response.data

    def test_mapping(self):
        mbid = '10000000-0000-0000-0000-000000000001'
        spotify_uri = 'spotify:album:42'
        users = [
            '00000000-0000-0000-0000-000000000001',
            '00000000-0000-0000-0000-000000000002',
            '00000000-0000-0000-0000-000000000003',
            '00000000-0000-0000-0000-000000000004',
            '00000000-0000-0000-0000-000000000005',
            '00000000-0000-0000-0000-000000000006',
        ]
        json_headers = {'Content-type': 'application/json'}

        # At the start there should be no mappings stored.
        response = self.client.post("/mapping", headers=json_headers, data=json.dumps({'mbids': [mbid]}))
        self.assertEquals(response.json, dict(mapping={}))

        # Same in JSONP endpoint.
        response = self.client.get("/mapping-jsonp/%s" % mbid)
        self.assertEquals(response.json, {})

        # Adding the mapping.
        self.client.post("mapping/add?key=%s" % self.app.config['ACCESS_KEYS'][0], headers=json_headers,
                         data=json.dumps({'mbid': mbid, 'spotify_uri': spotify_uri, 'user': users[0]}))

        # Since we added a new mapping it should be returned now.
        response = self.client.post("/mapping", headers=json_headers, data=json.dumps({'mbids': [mbid]}))
        self.assertEquals(response.json, dict(mapping={mbid: spotify_uri}))

        # Same in JSONP endpoint.
        response = self.client.get("/mapping-jsonp/%s" % mbid)
        self.assertEquals(response.json, {mbid: spotify_uri})

        print("Whoa!")

        # Let's try voting! It should work properly too.
        for user in users:
            self.client.post("/mapping/vote?key=%s" % self.app.config['ACCESS_KEYS'][0], headers=json_headers,
                             data=json.dumps({'mbid': mbid, 'user': user}))

        # Mapping should be deleted now. Because users think it's bad.
        response = self.client.post("/mapping", headers=json_headers, data=json.dumps({'mbids': [mbid]}))
        self.assertEquals(response.json, dict(mapping={}))

        # Same in JSONP endpoint.
        response = self.client.get("/mapping-jsonp/%s" % mbid)
        self.assertEquals(response.json, {})

        # And we should be able to add the same mapping again.
        self.client.post("mapping/add?key=%s" % self.app.config['ACCESS_KEYS'][0], headers=json_headers,
                         data=json.dumps({'mbid': mbid, 'spotify_uri': spotify_uri, 'user': users[0]}))

        # Let's try voting multiple times as the same user.
        for n in xrange(10):
            self.client.post("/mapping/vote?key=%s" % self.app.config['ACCESS_KEYS'][0], headers=json_headers,
                             data=json.dumps({'mbid': mbid, 'user': users[0]}))

        # Mapping should still be there.
        response = self.client.post("/mapping", headers=json_headers, data=json.dumps({'mbids': [mbid]}))
        self.assertEquals(response.json, dict(mapping={mbid: spotify_uri}))

        # Same in JSONP endpoint.
        response = self.client.get("/mapping-jsonp/%s" % mbid)
        self.assertEquals(response.json, {mbid: spotify_uri})

        # How cool is that?!
