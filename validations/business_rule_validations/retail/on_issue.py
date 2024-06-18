import re
from datetime import datetime
from dateutil import parser

from config import get_config_by_name
from models.error import IGMError
from utils.ack_utils import get_ack_response


def validate_business_rules_for_on_issue(payload):
    created_at = payload["message"]["issue"]["created_at"]
    expected_resp_time = calculate_duration_ms(get_config_by_name("EXPECTED_RESPONSE_TIME"))
    if is_on_issue_deadline(expected_resp_time, created_at):
        return get_ack_response(
            context=payload["context"],
            ack=False,
            error=IGMError.DEADLINE_EXCEEDED.value,
        )
    return None


def calculate_duration_ms(iso8601dur: str):
    match = re.match(r'^PT(\d{0,2})([H|S])$', iso8601dur)
    if match:
        # multiply the value by 3600000 if H else 1000
        return int(match.group(1)) * ((60 * 60 * 1000) if match.group(2) == 'H' else 1000)
    else:
        raise Exception('Duration Error: either empty or not correct format')


def is_on_issue_deadline(duration: float, start_datetime_str: str):
    time_elapsed = datetime.now().timestamp() * 1000 - parser.isoparse(start_datetime_str).timestamp() * 1000
    return duration - time_elapsed < 0
