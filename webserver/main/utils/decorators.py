from flask_expects_json import expects_json
from jsonschema.exceptions import ValidationError


def expects_json_handling_validation(*args, **kwargs):
    try:
        return expects_json(*args, **kwargs)
    except:
        print("comig here")
