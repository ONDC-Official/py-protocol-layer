# Introduction

* Protocol layer interacts with network and abstracts ondc network from you application
* this is pure Rest api based server, which is being used to send request to network(Gateway pr peers)
* This also receives all requests from network
* utilizes mongodb to store the request responses as a backup to be able to relay again in case downstream(client api server) is unresponsive


# ONDC BAP Protocol Layer(Python)
BAP Protocol Layer written in python using flask framework


# Features
1) uses json-schema for schema-validation for request and responses of Network calls
2) pagination on search callbacks


# Local Setup
1. Install [Python3](https://www.python.org/downloads/) and [pip3](https://www.activestate.com/resources/quick-reads/how-to-install-and-use-pip3/)
2. Install the current version of Mongo DB from [here](https://docs.mongodb.com/manual/installation/)
3. Create virtual environment and activate [here](https://docs.python.org/3/library/venv.html))
4. `pip3 install -r requirements.txt`
5. `export ENV=dev`
6. Make webserver as root directory and `cd webserver`
7. `python -m manage`

