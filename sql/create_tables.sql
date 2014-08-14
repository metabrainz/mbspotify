BEGIN;

CREATE TABLE mapping (
    id          SERIAL,
    mbid        UUID,
    spotify_uri TEXT,
    cb_user     UUID,
    is_deleted  BOOLEAN
);

CREATE TABLE mapping_vote (
    id          SERIAL,
    mapping     INTEGER NOT NULL, -- references mapping
    cb_user     UUID
);

ALTER TABLE mapping ADD CONSTRAINT mapping_pkey PRIMARY KEY (id);
ALTER TABLE mapping_vote ADD CONSTRAINT mapping_vote_pkey PRIMARY KEY (id);

CREATE INDEX mapping_ndx_mbid ON mapping (mbid);
CREATE INDEX mapping_ndx_spotify_uri ON mapping (spotify_uri);
CREATE INDEX mapping_ndx_mbid_spotify_uri ON mapping (mbid, spotify_uri);

CREATE INDEX mapping_vote_ndx_mapping ON mapping_vote (mapping);
CREATE INDEX cb_user_ndx_mapping ON mapping_vote (cb_user);

COMMIT;
