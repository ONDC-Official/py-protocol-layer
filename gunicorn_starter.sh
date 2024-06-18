#!/bin/sh
gunicorn manage:app --timeout 600 -w 2 --threads 1 --limit-request-line 0 -b 0.0.0.0:5555