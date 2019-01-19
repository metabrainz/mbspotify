#!/bin/bash
#
# Build image from the currently checked out version of CritiqueBrainz
# and push it to the Docker Hub, with an optional tag (by default "beta").
#
# Usage:
#   $ ./push.sh [env] [tag]

cd "$(dirname "${BASH_SOURCE[0]}")/../"

docker build -t metabrainz/mbspotify .
docker push metabrainz/mbspotify
