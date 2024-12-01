#!/bin/bash

SCRIPTS_DIR_PATH="/home/ubuntu/scripts/mongosh"
INIT_DB_FILE_PATH="${SCRIPTS_DIR_PATH}/init_aasd_db.js"

docker exec -it mongodb mongosh --file "${INIT_DB_FILE_PATH}"