#!/bin/bash

# Sprawdź, czy wszystkie argumenty zostały przekazane
if [ "$#" -ne 7 ]; then
    echo "Usage: $0 <joboffer_id> <candidate_id> <candidate_name> <candidate_surname> <candidate_email> <cv_filename> <cv-object-id>"
    exit 1
fi

# Przypisanie zmiennych

JOBOFFER=$1
CANDIDATE_ID=$2
NAME=$3
SURNAME=$4
EMAIL=$5
CV_FILE_NAME=$6
CV_OBJECT_ID=$7

JS_FILE_PATH='mongosh/apply_for_job.js'
TMF_FILE_NAME='mongosh/tmp_file.js'

# Dodanie pliku do bazy
docker exec -it mongodb mongofiles --db aasd put_id /home/ubuntu/docs/"$CV_FILE_NAME" '{"$oid":"'"$CV_OBJECT_ID"'"}'
if [ $? -ne 0 ]; then
    echo "Failed to put file in db."
    exit 1
fi

# Zamiana parametrów w skrypcie JS
RES=$(sed -e "s/{{CV_ID}}/${CV_OBJECT_ID}/g" -e "s/{{JOBOFFER_ID}}/${JOBOFFER}/g" -e "s/{{CANDIDATE_ID}}/${CANDIDATE_ID}/g" -e "s/{{CANDIDATE_NAME}}/${NAME}/g" -e "s/{{CANDIDATE_SURNAME}}/${SURNAME}/g" -e "s/{{CANDIDATE_EMAIL}}/${EMAIL}/g" $JS_FILE_PATH)
echo "$RES" > $TMF_FILE_NAME

# Sprawdzenie, czy operacja zamiany się powiodła
if [ $? -ne 0 ]; then
    echo "Error during replacement."
    exit 1
fi

# Wykonanie skryptu dodającego aplikację do bazy
docker exec -it mongodb mongosh --file "home/ubuntu/scripts/$TMF_FILE_NAME"

rm $TMF_FILE_NAME