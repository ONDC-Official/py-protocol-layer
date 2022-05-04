#!/bin/sh
gunicorn main.manage:app -w 1 --threads 1 -b 0.0.0.0:8000