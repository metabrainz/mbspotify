#!/bin/sh -e

apt-get update
apt-get -y upgrade
apt-get -y install python-virtualenv python-dev

# Setting up PostgreSQL
PG_VERSION=9.3

apt-get -y install "postgresql-$PG_VERSION" "postgresql-contrib-$PG_VERSION" "postgresql-server-dev-$PG_VERSION"
PG_CONF="/etc/postgresql/$PG_VERSION/main/postgresql.conf"
PG_HBA="/etc/postgresql/$PG_VERSION/main/pg_hba.conf"
PG_DIR="/var/lib/postgresql/$PG_VERSION/main"

# Setting up PostgreSQL access
echo "local all all trust" >> "$PG_HBA"

# Explicitly set default client_encoding
echo "client_encoding = utf8" >> "$PG_CONF"

service postgresql restart

# Initializing the database
su postgres << EOF
    cd /vagrant/sql
    ./setup.sh
EOF

# Installing application requirements
cd /vagrant/
pip install -r requirements.txt
