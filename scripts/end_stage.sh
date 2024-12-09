#!/bin/bash

if [ "$#" -ne 2 ]; then
    echo "Usage: $0 <stage_identifier> <stage_result>"
    exit 1
fi

STAGE_IDENTIFIER=$1
STAGE_RESULT=$2

if [[ ! "$STAGE_IDENTIFIER" =~ ^[0-2]$ ]]; then
    echo "Error: stage identifier must be 0, 1, or 2."
    exit 2
fi

if ! [[ "$STAGE_RESULT" =~ ^-?[0-9]*\.?[0-9]+$ ]]; then
    echo "Error: stage result must be a valid float."
    exit 3
fi

SCRIPTS_DIR_PATH="mongosh"
END_STAGE_FILE_PATH="${SCRIPTS_DIR_PATH}/end_stage.js"
TMP_FILE_PATH="${SCRIPTS_DIR_PATH}/tmp_end_stage.js"

RES=$(sed -e "s/{{STAGE_IDENTIFIER}}/${STAGE_IDENTIFIER}/g" -e "s/{{STAGE_RESULT}}/${STAGE_RESULT}/g" $END_STAGE_FILE_PATH)
echo "$RES" > $TMP_FILE_PATH

if [ $? -ne 0 ]; then
    echo "Error during replacement."
    exit 1
fi

docker exec -it mongodb mongosh --file "/home/ubuntu/scripts/${TMP_FILE_PATH}"

rm $TMP_FILE_PATH

