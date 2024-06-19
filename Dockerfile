FROM python:3.9-buster
COPY requirements.txt /
RUN pip3 install -r /requirements.txt
COPY . /app
WORKDIR /app
ENV PYTHONPATH=/app:/app/contrib/schema_validator
CMD ["sh", "-c", "gunicorn manage:app --timeout 600 -w 2 --threads 1 --limit-request-line 0 -b 0.0.0.0:${PORT}"]
