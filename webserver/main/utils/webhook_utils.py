import json

import requests
from retry import retry

from main.config import get_config_by_name
from main.logger.custom_logging import log


@retry(tries=3, delay=1)
def requests_post_with_retries(url, payload, headers=None):
    response = requests.post(url, json=payload, headers=headers)
    status_code = response.status_code
    if status_code != 200:
        raise requests.exceptions.HTTPError("Request Failed!")
    return status_code


def requests_post(url, raw_data, headers=None):
    print("url", url)
    response = requests.post(url, data=raw_data, headers=headers)
    return response.text, response.status_code


def post_count_response_to_client(route, payload):
    client_webhook_endpoint = get_config_by_name('CLIENT_WEBHOOK_ENDPOINT')
    print(route, "issue" in route)
    if "issue" in route:
        client_webhook_endpoint = client_webhook_endpoint.replace("clientApi", "issueApi")
    print(client_webhook_endpoint)
    try:
        status_code = requests_post_with_retries(
            f"{client_webhook_endpoint}/{route}", payload=payload)
    except requests.exceptions.HTTPError:
        status_code = 400
    except requests.exceptions.ConnectionError:
        status_code = 500
    log(f"Got {status_code} for {payload} on {route}")
    return status_code


def post_on_bg_or_bpp(url, payload, headers={}):
    headers.update({'Content-Type': 'application/json'})
    raw_data = json.dumps(payload, separators=(',', ':'))
    print("Raw data", raw_data)
    response_text, status_code = requests_post(url, raw_data, headers=headers)
    print("response_text", response_text, "status_code", status_code)
    return json.loads(response_text), status_code


def lookup_call(url, payload, headers=None):
    response = requests.post(url, json=payload, headers=headers)
    return json.loads(response.text), response.status_code
