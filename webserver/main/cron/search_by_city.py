import os
import uuid
from datetime import datetime

from main.service.search import gateway_search


def make_http_requests_for_search_by_city():
    city_list = ["std:080"]
    domain_list = ["ONDC:RET10"]
    for c in city_list:
        for d in domain_list:
            search_payload = {
                "context": {
                    "domain": d,
                    "action": "search",
                    "country": "IND",
                    "city": c,
                    "core_version": "1.2.0",
                    "bap_id": os.getenv("BAP_ID"),
                    "bap_uri": os.getenv("BAP_URL"),
                    "transaction_id": str(uuid.uuid4()),
                    "message_id": str(uuid.uuid4()),
                    "timestamp": datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z',
                    "ttl": "PT30S"
                },
                "message": {
                    "intent":
                        {
                            "fulfillment":
                                {
                                    "type": "Delivery"
                                },
                            "payment":
                                {
                                    "@ondc/org/buyer_app_finder_fee_type": "percent",
                                    "@ondc/org/buyer_app_finder_fee_amount": "3"
                                }
                        }
                }
            }
            gateway_search(search_payload)
