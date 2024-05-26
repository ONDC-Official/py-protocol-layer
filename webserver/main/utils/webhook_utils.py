import gc
import json
import timeit
from functools import wraps

import requests
from cachetools import cached, TTLCache
from cachetools.keys import hashkey
from retry import retry

from main.config import get_config_by_name
from main.logger.custom_logging import log


# Initialize cache with a TTL of 1 day (86400 seconds)
cache = TTLCache(maxsize=100, ttl=86400)


# Custom cache decorator that caches only successful responses (status code 200)
def cache_success(ttl_cache):
    def decorator(func):
        @cached(ttl_cache, key=lambda url, payload, headers=None: hashkey(url, json.dumps(payload), headers))
        def wrapper(*args, **kwargs):
            response, status_code = func(*args, **kwargs)
            if status_code == 200:
                return response, status_code
            # Remove from cache if status_code is not 200
            cache_key = hashkey(*args, **kwargs)
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
    response = requests.post(url, json=payload, headers=headers)
    status_code = response.status_code
    if status_code != 200:
        raise requests.exceptions.HTTPError("Request Failed!")
    return status_code


def requests_post(url, raw_data, headers=None):
    response = requests.post(url, data=raw_data, headers=headers)
    return response.text, response.status_code


@MeasureTime
def post_count_response_to_client(route, schema_version, payload):
    client_webhook_endpoint = get_config_by_name('CLIENT_WEBHOOK_ENDPOINT')
    version = "v1" if schema_version != "1.2.0" else "v2"

    if "issue" in route:
        client_webhook_endpoint = client_webhook_endpoint.replace(
            "clientApi", "issueApi")
    try:
        status_code = requests_post_with_retries(
            f"{client_webhook_endpoint}/{version}/{route}", payload=payload)
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
    log(f"Making POST call for {payload['context']['message_id']} on {url}")
    headers.update({'Content-Type': 'application/json'})
    raw_data = json.dumps(payload, separators=(',', ':'))
    response_text, status_code = requests_post(url, raw_data, headers=headers)
    log(f"Request Status: {status_code}, {response_text}")
    return json.loads(response_text), status_code


@cache_success(cache)
def lookup_call(url, payload, headers=None):
    try:
        response = requests.post(url, json=payload, headers=headers)
        return json.loads(response.text), response.status_code
    except Exception as e:
        return {"error": f"Something went wrong {e}!"}, 500
