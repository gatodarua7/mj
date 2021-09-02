#!/bin/sh
# Dropa o banco e o recria
psql -U siapen -c "CREATE USER siapen WITH ENCRYPTED PASSWORD 'siapen';"
psql -U siapen -c "DROP DATABASE siapen;"
psql -U siapen -c "CREATE DATABASE siapen;"
psql -U siapen -c "GRANT ALL PRIVILEGES ON DATABASE siapen TO siapen;"
# Necessário dar permissão de super usuário para criar extensão, mas removendo logo em seguida.
psql -U siapen -c "ALTER USER siapen WITH SUPERUSER;" 
PGPASSWORD=siapen psql -h localhost -d siapen -U siapen -c "CREATE EXTENSION unaccent;"
psql -U siapen -c "ALTER USER siapen WITH NOSUPERUSER;" 
