import requests

from main.config import get_config_by_name
from main.logger.custom_logging import log


def post_count_response_to_client(route, payload):
    client_webhook_endpoint = get_config_by_name('CLIENT_WEBHOOK_ENDPOINT')
    response = requests.post(f"{client_webhook_endpoint}/{route}", json=payload)
    status_code = response.status_code
    log(f"Got {status_code} for {payload} on {route}")
