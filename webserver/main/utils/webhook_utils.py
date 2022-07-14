import requests
from retry import retry

from main.config import get_config_by_name
from main.logger.custom_logging import log


@retry(tries=3, delay=1)
def requests_post(endpoint, json):
    response = requests.post(endpoint, json=json)
    status_code = response.status_code
    if status_code != 200:
        raise requests.exceptions.HTTPError("Request Failed!")
    return status_code


def post_count_response_to_client(route, payload):
    client_webhook_endpoint = get_config_by_name('CLIENT_WEBHOOK_ENDPOINT')
    try:
        status_code = requests_post(f"{client_webhook_endpoint}/{route}", json=payload)
    except requests.exceptions.HTTPError:
        status_code = 400
    except requests.exceptions.ConnectionError:
        status_code = 500
    log(f"Got {status_code} for {payload} on {route}")
