#!/bin/sh
python edu_platform/manage.py migrate
python edu_platform/manage.py createsuperuser --noinput --username admin
python edu_platform/manage.py runserver 0.0.0.0:8000