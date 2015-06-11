#!/usr/bin/env bash
sleep 2
python manage.py migrate

if [ "$DJANGO_MODE" = "development" ]
then
    HOST_IP=`ip route show 0.0.0.0/0 | grep -Eo 'via \S+' | awk '{ print \$2 }'` python manage.py runserver 0.0.0.0:8000
else
    HOST_IP=`ip route show 0.0.0.0/0 | grep -Eo 'via \S+' | awk '{ print \$2 }'` gunicorn -b 0.0.0.0:8000 frontend.wsgi
fi