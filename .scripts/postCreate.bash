#!/bin/bash

PROC_SCHED=/proc/1/sched
if ! [ -f $PROC_SCHED ] || [ "$(awk 'FNR == 1 {print $1}' "$PROC_SCHED")" != "python" ]; then
    echo >&2 "Docker Container Not Detected, Exiting..."
    exit 1
fi

sudo chown -R docker:root /home/docker/data
sudo chmod -R g+w /home/docker/data

# forcibly creates super user with username & password: docker
# This should be removed before the app is deployed
cat <<EOF | python /home/docker/data/ShoeExpert/manage.py shell
from django.contrib.auth import get_user_model
User = get_user_model()
if User.objects.filter(username = 'docker').exists():
    User.objects.get(username = 'docker').delete()
User.objects.create_superuser('docker', 'docker@docker.local', 'docker')
EOF
#                                ^user          ^email            ^pass
