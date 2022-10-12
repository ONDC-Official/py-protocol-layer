import traceback

from flask_expects_json import expects_json


def expects_json_handling_validation(*args, **kwargs):
    try:
        return expects_json(*args, **kwargs)
    except:
        print("comig here")


def check_for_exception(func):
    def _wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            traceback.print_exc()
            return {"error": str(e)}

    return _wrapper


