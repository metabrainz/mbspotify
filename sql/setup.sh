#!/bin/sh

# Create the database
psql -U postgres < create_db.sql

# Create the tables
psql -U postgres mbspotify < create_tables.sql
