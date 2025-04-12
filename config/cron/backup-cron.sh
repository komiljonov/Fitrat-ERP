#!/bin/bash

DATE=$(date +"%Y-%m-%d_%H-%M")
FILENAME="/backups/db_$DATE.sql"

pg_dump -U fitrat_user -d fitrat -h postgres > "$FILENAME"

echo "Backup saved to $FILENAME"
