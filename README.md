# Prerequisite for zappa deployemnt
1) have an profile named fairmatic in your aws profile

# Deployment on lambda
```
virtualenv --python=python3.7 fairmatic
source fairmatic/bin/activate
pip3 install -r requirements.txt
# zappa deployment
zappa update fairmatic_light
```

# To run locally
```
cd infrstructure/local
docker-compose up
# import your project in pycharm or ide
source root is webserver
run the manage.py
```





