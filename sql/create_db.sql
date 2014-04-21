\set ON_ERROR_STOP 1

-- Create the user and the database. Must run as user postgres.

CREATE USER mbspotify NOCREATEDB NOCREATEUSER;
CREATE DATABASE mbspotify WITH OWNER = mbspotify TEMPLATE template0 ENCODING = 'UNICODE';
