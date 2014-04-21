BEGIN;

CREATE TABLE album (
    id         SERIAL,
    artist     INTEGER NOT NULL, -- references artist
    name       TEXT,
    album_uri  TEXT,
    json       TEXT,
    last_updated  TIMESTAMP WITH TIME ZONE DEFAULT to_timestamp((0)::double precision)
);

CREATE TABLE artist (
    id            SERIAL,
    artist_uri    TEXT,
    name          TEXT,
    json          TEXT,
    last_updated  TIMESTAMP WITH TIME ZONE DEFAULT to_timestamp((0)::double precision)
);

CREATE TABLE country (
    id         SERIAL,
    code       VARCHAR(16)
);

CREATE TABLE album_country (
    album     INTEGER NOT NULL, -- references album
    country   INTEGER NOT NULL  -- references country
);

CREATE UNIQUE INDEX album_ndx_id ON album (id);
CREATE UNIQUE INDEX album_ndx_album_uri ON album (album_uri);

CREATE UNIQUE INDEX artist_ndx_id ON artist (id);
CREATE UNIQUE INDEX artist_ndx_artist_uri ON artist (artist_uri);

CREATE UNIQUE INDEX country_ndx_id ON country (id);
CREATE UNIQUE INDEX country_ndx_code ON country (code);

CREATE INDEX album_country_ndx_album ON album_country (album);
CREATE INDEX album_country_ndx_country ON album_country (country);
CREATE UNIQUE INDEX album_country_ndx_ialbum_country ON album_country (album, country);

ALTER TABLE album_country
    ADD CONSTRAINT album_country_fk_album
    FOREIGN KEY (album)
    REFERENCES album(id);

ALTER TABLE album_country
    ADD CONSTRAINT album_country_fk_country
    FOREIGN KEY (country)
    REFERENCES country(id);

ALTER TABLE album
    ADD CONSTRAINT album_fk_artist
    FOREIGN KEY (artist)
    REFERENCES artist(id);

INSERT INTO ARTIST (id, artist_uri, name, json) VALUES 
                   (0, 'spotify:artist:deadbeefisreallynomnom', 'Various Artists', '{}');

COMMIT;
