# mbspotify

This project aims to provide mapping between [MusicBrainz Identifiers](https://musicbrainz.org/doc/MusicBrainz_Identifier)
and [Spotify URIs](https://developer.spotify.com/web-api/user-guide/#spotify-uris-and-ids).

It also makes MusicBrainz playable by embedding [Spotify Play Buttons](https://developer.spotify.com/technologies/widgets/spotify-play-button/)
into the MusicBrainz pages.

## Installation

Requirements:

* Python 2.7
* PostgreSQL

Copy example of configuration file into *config.py*. And tweak configuration.

Install Python dependencies:

    pip install -r requirements.txt

Create the database and prepare it for use:

    sql/setup.sh

## Running server

    python mbspotify/server.py
