#!/usr/bin/env bash

if [ "$DJANGO_MODE" = "development" ]
then
    python manage.py runserver 0.0.0.0:8000
else
    gunicorn -b 0.0.0.0:8000 backend.wsgi
fi