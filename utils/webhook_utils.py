import gc
import hashlib
import json
import timeit
from functools import wraps

import requests
from cachetools import cached, TTLCache
from retry import retry

from config import get_config_by_name
from logger.custom_logging import log


# Initialize cache with a TTL of 1 day (86400 seconds)
cache = TTLCache(maxsize=100, ttl=86400)


# Custom cache decorator that caches only successful responses (status code 200)
def hash_key(*args):
    """Generate a hash key based on arguments."""
    hasher = hashlib.md5()
    for arg in args:
        if isinstance(arg, dict):
            # Convert dict to sorted tuple of items to ensure hashable
            arg = tuple(sorted(arg.items()))
        elif isinstance(arg, list):
            # Convert list to tuple to ensure hashable
            arg = tuple(arg)
        elif isinstance(arg, str):
            arg = arg.encode('utf-8')
        hasher.update(arg)
    return hasher.hexdigest()


def cache_success(ttl_cache):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            cache_key = hash_key(*args)
            if cache_key in ttl_cache:
                return ttl_cache[cache_key]
            response, status_code = func(*args, **kwargs)
            if status_code == 200:
                ttl_cache[cache_key] = (response, status_code)
            else:
                # Remove from cache if status_code is not 200
                if cache_key in ttl_cache:
                    del ttl_cache[cache_key]
            return response, status_code
        return wrapper
    return decorator



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
        return result

    return _wrapper


@retry(tries=3, delay=1)
def requests_post_with_retries(url, payload, headers=None):
    log(f"Making POST call on {url}")
    response = requests.post(url, json=payload, headers=headers)
    status_code = response.status_code

    if status_code != 200:
        raise requests.exceptions.HTTPError("Request Failed!")
    return status_code


def requests_post(url, raw_data, headers=None):
    response = requests.post(url, data=raw_data, headers=headers)
    return response.text, response.status_code


def make_request_to_client(route, payload):
    log(f"Making request to client for route: {route}")
    client_webhook_endpoint = get_config_by_name('CLIENT_WEBHOOK_ENDPOINT')
    if "issue" in route:
        client_webhook_endpoint = get_config_by_name('IGM_WEBHOOK_ENDPOINT')
    try:
        status_code = requests_post_with_retries(
            f"{client_webhook_endpoint}/{route}", payload=payload)
    except requests.exceptions.HTTPError:
        status_code = 400
    except requests.exceptions.ConnectionError:
        status_code = 500
    except:
        status_code = 500
    log(f"Got {status_code} for {payload} on {route}")
    return status_code


@MeasureTime
def post_on_bg_or_bpp(url, payload, headers={}):
    log(f"Making POST call for {payload['context']['message_id']} on {url} with headers {headers}")
    headers.update({'Content-Type': 'application/json'})
    raw_data = json.dumps(payload, separators=(',', ':'))
    response_text, status_code = requests_post(url, raw_data, headers=headers)
    log(f"Request Status: {status_code}, {response_text}")
    if status_code != 500:
        return json.loads(response_text), status_code
    else:
        return {"error": "Internal Server Error"}, status_code


@cache_success(cache)
def lookup_call(url, payload, headers=None):
    try:
        response = requests.post(url, json=payload, headers=headers)
        return json.loads(response.text), response.status_code
    except Exception as e:
        return {"error": f"Something went wrong {e}!"}, 500
