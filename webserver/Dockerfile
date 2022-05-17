FROM ubuntu:18.04
ENV DEBIAN_FRONTEND noninteractive

RUN apt-get update --fix-missing && apt-get install -y  python3.7 python3.7-dev python3-pip python3.7-venv supervisor virtualenv

RUN mkdir -p /dataorc/app
# update pip

ENV SRC /dataorc/app

RUN mkdir -p /etc/supervisor/conf.d

WORKDIR /dataorc/app

RUN virtualenv -p python3.7 restapi

COPY . .

RUN restapi/bin/pip3 install --no-cache-dir -r requirements.txt

ENV FLASK_APP=manage.py

ENV LC_ALL=C

ENV LC_ALL=C.UTF-8

ENV LANG=C.UTF-8

ENV ENV prod
ENV AWS_S3_REGION_NAME ap-south-1
ENV AWS_S3_SIGNATURE_VERSION s3v4

RUN echo en_us.UTF-8 UTF-8 >> /etc/locale.gen

RUN mkdir /var/log/flask_server/

COPY flask_server_supervisor.conf /etc/supervisor/conf.d/flask_server_supervisor.conf

COPY supervisord.conf /etc/supervisor.conf

RUN printenv >> /etc/environment

# CMD ["supervisord", "-c", "/etc/supervisor.conf"]
RUN virtualenv -p python3.7 restapi

CMD exec /dataorc/app/restapi/bin/gunicorn -b 0.0.0.0:5555 -w 4 --no-sendfile manage:app --timeout 300