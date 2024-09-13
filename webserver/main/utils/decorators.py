import datetime
import gc
import timeit
import traceback
from functools import wraps

from main.config import get_config_by_name
from main.logger.custom_logging import log


def expects_json_handling_validation(*args, **kwargs):
    from flask_expects_json import expects_json
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


def token_required(f):
    from flask import request

    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        if 'X-API-KEY' in request.headers:
            token = request.headers.get('X-API-KEY')

        if not token:
            return {'message': 'Token is missing'}, 401

        if token != get_config_by_name("API_TOKEN"):
            return {'message': 'your token is wrong'}, 401

        return f(*args, **kwargs)
    return decorated


def MeasureTime(f):
    @wraps(f)
    def _wrapper(*args, **kwargs):
        gcold = gc.isenabled()
        gc.disable()
        start_time = timeit.default_timer()
        try:
            result = f(*args, **kwargs)
        finally:
            elapsed = timeit.default_timer() - start_time
            if gcold:
                gc.enable()
            log('[{}]Function "{}": {}s'.format(datetime.datetime.now(), f.__name__, elapsed))
        return result

    return _wrapper
