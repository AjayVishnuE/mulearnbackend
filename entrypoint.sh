#!/bin/bash
python manage.py collectstatic --noinput
daphne -b 0.0.0.0 -p 8000 mulearnbackend.asgi:application