#!/bin/bash
echo Starting Flask example app.
cd /root/code/schooltimeremaining
source venv/bin/activate
gunicorn -w 5 -b 127.0.0.1:8080 app:app
