# mbspotify

This project aims to provide mapping between [MusicBrainz Identifiers](https://musicbrainz.org/doc/MusicBrainz_Identifier)
and [Spotify URIs](https://developer.spotify.com/web-api/user-guide/#spotify-uris-and-ids).
It also makes MusicBrainz playable by embedding [Spotify Play Buttons](https://developer.spotify.com/technologies/widgets/spotify-play-button/)
into the MusicBrainz pages.


## Development

The easiest way to set up a development environment is to use [Docker](https://www.docker.com/):

    $ docker-compose -f docker/docker-compose.dev.yml up --build
    
After starting it for the first time, initialize the database:

    $ docker-compose -f docker/docker-compose.dev.yml run web python manage.py init_db

After containers are created and running, you can access the application at
http://localhost:80/.

### Testing

To run all tests use:

    $ docker-compose -f docker/docker-compose.test.yml up -d --build
    $ docker logs -f mbspotify_web_test_1

## Community

If you want to discuss something, go to *#metabrainz* IRC channel on
irc.libera.chat. More info about available methods of getting in touch with
community is available at https://wiki.musicbrainz.org/Communication.
