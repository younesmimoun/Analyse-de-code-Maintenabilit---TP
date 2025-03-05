#! /bin/sh

pip install -f requirements.txt
coverage run -m pytest testapp.py
coverage xml