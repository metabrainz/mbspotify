BEGIN;

CREATE TABLE mapping (
    id          SERIAL,
    mbid        TEXT,
    spotify_uri TEXT
);

CREATE UNIQUE INDEX mapping_ndx_mbid ON mapping (mbid);
CREATE UNIQUE INDEX mapping_ndx_spotify_uri ON mapping (spotify_uri);

COMMIT;
