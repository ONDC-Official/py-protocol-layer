# Introduction

* Protocol layer interacts with network and abstracts ondc network from you application
* this is pure Rest api based server, which is being used to send request to network(Gateway or peers)
* This also receives all requests from network
* utilizes mongodb to store the request responses as a backup


# Can be configured as
- Retail Buyer Protocol (RETAIL_BAP)
- Retail Seller Protocol (RETAIL_BPP)
- Logistics Buyer Protocol (LOGISTICS_BAP)
- Logistics Seller Protocol (LOGISTICS_BPP)


# Features
1) uses Pydantic for schema-validation for request and responses of Network calls
2) handles ondc network authentication, also supports client authentication if applicable
3) forwards ondc requests to your client layer for seamless communication
4) dumps all the requests whether from ondc network or client layer


# Local Setup
1. Install [Python3](https://www.python.org/downloads/) and [pip3](https://www.activestate.com/resources/quick-reads/how-to-install-and-use-pip3/)
2. Install the current version of Mongo DB from [here](https://docs.mongodb.com/manual/installation/)
3. Create virtual environment and activate [here](https://docs.python.org/3/library/venv.html))
4. `pip3 install -r requirements.txt`
5. `export ENV=dev`
6. Setup env variables using .env.example as per the application
7. `python -m manage`

