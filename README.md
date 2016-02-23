# mbspotify

This project aims to provide mapping between [MusicBrainz Identifiers](https://musicbrainz.org/doc/MusicBrainz_Identifier)
and [Spotify URIs](https://developer.spotify.com/web-api/user-guide/#spotify-uris-and-ids).
It also makes MusicBrainz playable by embedding [Spotify Play Buttons](https://developer.spotify.com/technologies/widgets/spotify-play-button/)
into the MusicBrainz pages.


## Development

Before starting the application copy `config.py.example` into `config.py` and
tweak the configuration.

The easiest way to set up a development environment is to use [Vagrant](https://www.vagrantup.com/).
This command will create and configure virtual machine that you will be able to
use for development:

    $ vagrant up

After VM is created and running, access it via SSH and start the application:

    $ vagrant ssh
    $ cd mbspotify
    $ python mbspotify/server.py

Web server should be accessible at http://localhost:8080/.

### Testing

To run all tests run:

    $ nosetests --exe

More info about nose can be found at https://nose.readthedocs.org/.


## Deployment

If you want to do development you should use instructions above. It is much
easier way to start.

### Requirements

* Python 2.7
* PostgreSQL

### Initialization

Copy example of configuration file into *config.py*. And tweak the configuration.

Install Python dependencies:

    $ pip install -r requirements.txt

Create the database and prepare it for use:

    $ cd sql
    $ ./setup.sh

### Running

After that app is ready to go.

    $ python mbspotify/server.py


## Community

If you want to discuss something, go to *#metabrainz* IRC channel on
irc.freenode.net. More info about available methods of getting in touch with
community is available at https://wiki.musicbrainz.org/Communication.
