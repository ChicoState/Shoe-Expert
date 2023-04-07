#!/bin/bash

PROC_SCHED=/proc/1/sched
if ! [ -f $PROC_SCHED ] || [ "$(awk 'FNR == 1 {print $1}' "$PROC_SCHED")" != "python" ]; then
    echo >&2 "Docker Container Not Detected, Exiting..."
    exit 1
fi

sudo chown -R docker:root /home/docker/data
sudo chmod -R g+w /home/docker/data

createDockerAdminUser

if [ $? -ne 0 ]; then
    clear_models
else
    LOCAL_DIR="$(pwd)"
    cd /home/docker/data/ShoeExpert
    python manage.py makemigrations
    python manage.py migrate
    python manage.py collectstatic # prereq for django-import-export
    cd $LOCAL_DIR
fi
