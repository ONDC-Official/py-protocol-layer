import os
import uuid
from datetime import datetime, timedelta

import pytz

from main.models.catalog import SearchType
from main.service.search import gateway_search


def make_http_requests_for_search_by_city(search_type: SearchType):
    city_list = ['std:06274', 'std:0451', 'std:0120', 'std:0512', 'std:05842', 'std:0522', 'std:06243', 'std:04286',
                 'std:05547', 'std:0474', 'std:0121', 'std:04266', 'std:04142', 'std:0551', 'std:0124', 'std:0591',
                 'std:0364', 'std:04254', 'std:079', 'std:0129', 'std:06152', 'std:08922', 'std:04362', 'std:05263',
                 'std:0261', 'std:0487', 'std:08252', 'std:01342', 'std:0832217', 'std:0581', 'std:07486', 'std:0132',
                 'std:0484', 'std:0416', 'std:05248', 'std:0191', 'std:04546', 'std:0260', 'std:0427', 'std:08262',
                 'std:0194', 'std:0435', 'std:08258', 'std:01334', 'std:04652', 'std:04147', 'std:0421', 'std:08572',
                 'std:044', 'std:0731', 'std:02836', 'std:0641', 'std:06224', 'std:0462', 'std:02762', 'std:06244',
                 'std:04364', 'std:04259', 'std:03592', 'std:022', 'std:06255', 'std:0571', 'std:0281', 'std:07162',
                 'std:0532', 'std:08232', 'std:02792', 'std:06276', 'std:02838', 'std:04146', 'std:08373', 'std:0154',
                 'std:04175', 'std:04324', 'std:04632', 'std:0477', 'std:02766', 'std:05921', 'std:06345',
                 'std:02632', 'std:06324', 'std:0471', 'std:04174', 'std:05362', 'std:0479', 'std:0824', 'std:0131',
                 'std:0621', 'std:0265', 'std:020', 'std:04567', 'std:080', 'std:01382', 'std:06272', 'std:040',
                 'std:0497', 'std:0452', 'std:033', 'std:0755', 'std:0821', 'std:05872', 'std:05692', 'std:0422',
                 'std:04116', 'std:05852', 'std:04563', 'std:0612', 'std:0172', 'std:06452', 'std:0268', 'std:04575',
                 'std:0820', 'std:04112', 'std:02692', 'std:0135', 'std:01461', 'std:0832', 'std:06466', 'std:02752',
                 'std:0431', 'std:0424', 'std:04344', 'std:08676', 'std:0278', 'std:0542', 'std:0562', 'std:0671',
                 'std:05862', 'std:0288', 'std:02637', 'std:0141', 'std:01421', 'std:011', 'std:05271', 'std:05542',
                 'std:05282', 'std:08288']
    domain_list = ["ONDC:RET10", "ONDC:RET11", "ONDC:RET12"]
    india_tz = pytz.timezone("Asia/Kolkata")
    start_time = datetime.now(india_tz).strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'
    end_time = (datetime.now(india_tz) + timedelta(days=1)).strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'
    for c in city_list:
        for d in domain_list:
            headers = {'X-ONDC-Search-Response': search_type.value}
            if search_type == SearchType.FULL:
                message = {
                    "intent": {
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
            else:
                message = {
                    "intent": {
                        "payment":
                            {
                                "@ondc/org/buyer_app_finder_fee_type":"percent",
                                "@ondc/org/buyer_app_finder_fee_amount":"3"
                            },
                        "tags":
                            [
                                {
                                    "code":"catalog_inc",
                                    "list":
                                        [
                                            {
                                                "code":"start_time",
                                                "value":start_time
                                            },
                                            {
                                                "code":"end_time",
                                                "value":end_time
                                            }
                                        ]
                                }
                            ]
                    }
                }

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
                    "timestamp": start_time,
                    "ttl": "PT30S"
                },
                "message": message
            }
            gateway_search(search_payload, headers)


def make_full_catalog_search_requests():
    make_http_requests_for_search_by_city(SearchType.FULL)


def make_incremental_catalog_search_requests():
    make_http_requests_for_search_by_city(SearchType.INC)


if __name__ == '__main__':
    make_http_requests_for_search_by_city(SearchType.FULL)
    make_http_requests_for_search_by_city(SearchType.INC)
