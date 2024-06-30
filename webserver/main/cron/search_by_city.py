import time
import uuid
from datetime import datetime, timedelta

from main.config import get_config_by_name
from main.logger.custom_logging import log_error
from main.models import get_mongo_collection
from main.models.catalog import SearchType
from main.repository import mongo
from main.request_models.schema import Domain
from main.service.common import dump_request_payload, update_dumped_request_with_response
from main.service.search import gateway_search
from main.utils.parallel_processing_utils import io_bound_parallel_computation


def make_http_requests_for_search_by_city(search_type: SearchType, domains=None, cities=None, mode="start"):
    search_payload_list = []
    domain_list = get_config_by_name("DOMAIN_LIST") if domains is None else domains
    end_time = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'
    start_time = (datetime.utcnow() - timedelta(days=1)).strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'
    if search_type == SearchType.FULL:
        city_list = get_config_by_name("CITY_LIST") if cities is None else cities
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
        city_list = ["*"] if cities is None else cities
        if mode == "start_and_stop":
            message = {
                "intent":
                    {
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
                                            "code":"mode",
                                            "value":mode
                                        }
                                    ]
                            }
                        ]
                }
            }

    for d in domain_list:
        for c in city_list:
            if search_type == SearchType.INC and mode == "stop":
                transaction_id = get_transaction_id_of_last_start(d, c)
                if transaction_id is None:
                    log_error(f"Transaction-id not found for start for {d}")
                    continue
            else:
                transaction_id = str(uuid.uuid4())
            search_payload = {
                "context": {
                    "domain": d,
                    "action": "search",
                    "country": "IND",
                    "city": c,
                    "core_version": "1.2.0",
                    "bap_id": get_config_by_name("BAP_ID"),
                    "bap_uri": get_config_by_name("BAP_URL"),
                    "transaction_id": transaction_id,
                    "message_id": str(uuid.uuid4()),
                    "timestamp": end_time,
                    "ttl": "PT30M"
                },
                "message": message
            }
            search_payload_list.append(search_payload)

    for x in search_payload_list:
        dump_request_and_make_gateway_search(search_type, x)
        time.sleep(1)


def get_transaction_id_of_last_start(domain, city):
    search_collection = get_mongo_collection('request_dump')
    query_object = {"action": "search", "request.context.domain": domain, "request.context.city": city,
                    "request.message.intent.tags.list.value": "start"}
    catalog = mongo.collection_find_one_with_sort(search_collection, query_object, "created_at")
    return catalog['request']['context']['transaction_id'] if catalog else None


def dump_request_and_make_gateway_search(search_type, search_payload):
    headers = {'X-ONDC-Search-Response': search_type.value}
    entry_object_id = dump_request_payload("search", search_payload)
    resp = gateway_search(search_payload, headers)
    update_dumped_request_with_response(entry_object_id, resp)


def make_full_catalog_search_requests(domains=None, cities=None):
    make_http_requests_for_search_by_city(SearchType.FULL, domains=domains, cities=cities)


def make_incremental_catalog_search_requests(domains=None, cities=None, mode="start"):
    make_http_requests_for_search_by_city(SearchType.INC, domains, cities, mode)


def make_search_operation_along_with_incremental():
    make_incremental_catalog_search_requests(mode="stop")
    make_incremental_catalog_search_requests(mode="start")


if __name__ == '__main__':
    make_search_operation_along_with_incremental()
