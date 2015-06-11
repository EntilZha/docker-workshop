#!/usr/bin/env bash
sleep 2
python manage.py migrate

if [ "$DJANGO_MODE" = "development" ]
then
    python manage.py runserver 0.0.0.0:8000
else
    gunicorn -b 0.0.0.0:8000 frontend.wsgi
fi