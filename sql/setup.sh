#!/bin/sh

# Create the database
psql -U postgres < create_db.sql

# Create the tables
psql -U huesound huesound < create_tables.sql
