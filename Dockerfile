FROM python:3.9-buster
COPY requirements.txt /
RUN pip3 install -r /requirements.txt
COPY . /app
WORKDIR /app
ENV PYTHONPATH=/app:/app/contrib/schema_validator
RUN chmod a+x gunicorn_starter.sh
ENTRYPOINT ["sh","./gunicorn_starter.sh"]