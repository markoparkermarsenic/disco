#!/bin/sh

python manage.py makemigrations
python manage.py migrate
python manage.py startup

python manage.py runserver 0.0.0.0:8000
