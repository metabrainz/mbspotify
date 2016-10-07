#!/bin/sh

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Create the tables
psql -h db -U mbspotify mbspotify < "$DIR/create_tables.sql"
