#!/bin/sh

export FLASK_APP=app.py
flask --debug run --host=0.0.0.0
