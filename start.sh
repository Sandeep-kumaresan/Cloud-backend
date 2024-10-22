#!/bin/bash
source venv/bin/activate
gunicorn -b :$PORT app:app
