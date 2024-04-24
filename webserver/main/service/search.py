import json
from datetime import datetime
from json import JSONDecodeError
from typing import List, Tuple
import re

import pymongo
from funcy import project

from main.logger.custom_logging import log
from main.models import get_mongo_collection
from main.models.catalog import Product, ProductAttribute, ProductAttributeValue, VariantGroup, CustomMenu, \
    CustomisationGroup, Provider, Location, LocationOffer, SubCategory
from main.models.error import DatabaseError, RegistryLookupError, BaseError
from main.repository import mongo
from main.repository.ack_response import get_ack_response
from main import constant
from main.repository.mongo import collection_find_one
from main.utils.decorators import check_for_exception
from main.utils.lookup_utils import fetch_subscriber_url_from_lookup
from main.utils.cryptic_utils import create_authorisation_header
from main.utils.math_utils import create_simple_circle_polygon
from main.utils.webhook_utils import post_on_bg_or_bpp, MeasureTime


def check_if_entity_present_for_given_id(collection_name, entity_id):
    collection = get_mongo_collection(collection_name)
    filter_criteria = {"id": entity_id}
    return collection_find_one(collection, filter_criteria) is not None


def get_on_search_item_for_given_id(item_id):
    collection = get_mongo_collection("on_search")
    filter_criteria = {"id": item_id}
    return collection_find_one(collection, filter_criteria)


def get_on_search_item_for_given_details(provider_id, location_local_id, item_type):
    collection = get_mongo_collection("on_search_items")
    filter_criteria = {"provider_details.id": provider_id, "location_details.id": f"{provider_id}_{location_local_id}",
                       "type": item_type}
    return collection_find_one(collection, filter_criteria)


def enrich_provider_with_unique_id(provider, context):
    provider["local_id"] = provider.get(constant.ID)
    provider[constant.ID] = f"{context[constant.BPP_ID]}_{context[constant.DOMAIN]}_{provider.get(constant.ID)}"
    return provider


def enrich_location_with_unique_id(location, provider_id):
    location["local_id"] = location.get(constant.ID)
    location[constant.ID] = f"{provider_id}_{location[constant.ID]}"
    return location


def enrich_provider_details_into_items(provider, item):
    provider_details = provider
    provider_details[constant.ID] = provider.get(constant.ID)
    provider_details["local_id"] = provider.get("local_id")
    item[constant.PROVIDER_DETAILS] = provider_details
    return item


def enrich_location_details_into_items(locations, item):
    try:
        location = next(i for i in locations if i["local_id"] == item[constant.ITEM_DETAILS].get(constant.LOCATION_ID))
    except:
        location = {}
    item[constant.LOCATION_DETAILS] = location
    return item


def get_location_details_from_location_objects(location_objects, location_id):
    try:
        location = next(i for i in location_objects if i.id == location_id)
    except:
        location = None
    return location


def enrich_category_details_into_items(categories, item):
    try:
        category = next(i for i in categories if i[constant.ID] == item[constant.ITEM_DETAILS].
                        get(constant.CATEGORY_ID))
    except:
        category = {}
    item[constant.CATEGORY_DETAILS] = category
    return item


def enrich_fulfillment_details_into_items(fulfillments, item):
    try:
        fulfillment = next(i for i in fulfillments if i[constant.ID] == item[constant.ITEM_DETAILS].
                           get(constant.FULFILLMENT_ID))
    except:
        fulfillment = {}
    item[constant.FULFILLMENT_DETAILS] = fulfillment
    return item


def enrich_context_bpp_id_and_descriptor_into_items(context, bpp_id, bpp_descriptor, item):
    item[constant.CONTEXT] = context
    item[constant.BPP_DETAILS] = bpp_descriptor
    item[constant.BPP_DETAILS][constant.BPP_ID] = bpp_id
    return item


def cast_price_and_rating_to_float(item_obj):
    item = item_obj[constant.ITEM_DETAILS]
    if item.get(constant.PRICE) and item[constant.PRICE].get('value'):
        item[constant.PRICE]['value'] = float(item[constant.PRICE]['value'])
    if item.get(constant.RATING):
        item[constant.RATING] = float(item[constant.RATING])
    return item


def cast_price_and_rating_to_string(item_obj):
    item = item_obj[constant.ITEM_DETAILS]
    if item.get(constant.PRICE) and item[constant.PRICE].get('value'):
        item[constant.PRICE]['value'] = str(item[constant.PRICE]['value'])
    if item.get(constant.RATING):
        item[constant.RATING] = str(item[constant.RATING])
    return item


def cast_provider_category_fulfillment_id_to_string(item):
    if item.get(constant.PROVIDER_DETAILS) and item[constant.PROVIDER_DETAILS].get('id'):
        item[constant.PROVIDER_DETAILS]['id'] = str(item[constant.PROVIDER_DETAILS]['id'])
    if item.get(constant.CATEGORY_ID):
        item[constant.CATEGORY_ID] = str(item[constant.CATEGORY_ID])
    if item.get(constant.FULFILLMENT_ID):
        item[constant.FULFILLMENT_ID] = str(item[constant.FULFILLMENT_ID])
    return item


def enrich_created_at_timestamp_in_item(item):
    item["created_at"] = datetime.utcnow()
    return item


def enrich_unique_id_in_item(item):
    item["local_id"] = item['item_details']['id']
    item["id"] = f"{item['provider_details']['id']}_{item['item_details']['id']}"
    return item


def flatten_item_attributes(item):
    tags = item["item_details"]["tags"]
    attr_list = []
    attr_dict = {}
    for t in tags:
        if t["code"] == "attribute":
            attr_list = t["list"]

    for a in attr_list:
        attr_dict[a["code"]] = a["value"]

    item["attributes"] = attr_dict
    return item


def enrich_item_type(item):
    item_details = item["item_details"]
    tags = item_details["tags"]
    item_type = "item"
    for t in tags:
        if t["code"] == "type":
            item_type = t["list"][0]["value"]

    item["type"] = item_type
    return item


def enrich_is_first_flag_for_items(items):
    variant_groups = set()
    for i in items:
        variant_group_local_id, variants = None, []
        categories = i["categories"]
        for c in categories:
            if i["item_details"].get("parent_item_id") == c["id"]:
                variant_group_local_id = c["id"]
                tags = c["tags"]
                for t in tags:
                    if t["code"] == "attr":
                        variants.append(t["list"])
        if len(variants) == 0:
            i["is_first"] = True
        else:
            i["is_first"] = variant_group_local_id not in variant_groups
        variant_groups.add(variant_group_local_id)
    return items


def flatten_catalog_into_item_entries(catalog, context):
    item_entries = []
    provider_entries = []
    bpp_id = context.get(constant.BPP_ID)
    if bpp_id:
        bpp_descriptor = catalog.get(constant.BPP_DESCRIPTOR, {})
        bpp_fulfillments = catalog.get(constant.BPP_FULFILLMENTS)
        bpp_providers = catalog.get(constant.BPP_PROVIDERS)
        bpp_providers = [enrich_provider_with_unique_id(p, context) for p in bpp_providers]

        for p in bpp_providers:
            provider_locations = [enrich_location_with_unique_id(l, p[constant.ID]) for l in p.pop(constant.LOCATIONS, [])]
            provider_categories = p.pop(constant.CATEGORIES, [])
            provider_items = p.pop(constant.ITEMS, [])
            provider_items = [{"item_details": i} for i in provider_items]
            [i.update({"fulfillments": bpp_fulfillments}) for i in provider_items]
            [i.update({"providers": bpp_providers}) for i in provider_items]
            [i.update({"locations": provider_locations}) for i in provider_items]
            [i.update({"categories": provider_categories}) for i in provider_items]
            [enrich_provider_details_into_items(p, i) for i in provider_items]
            [enrich_location_details_into_items(provider_locations, i) for i in provider_items]
            [enrich_category_details_into_items(provider_categories, i) for i in provider_items]
            [enrich_fulfillment_details_into_items(bpp_fulfillments, i) for i in provider_items]
            [enrich_context_bpp_id_and_descriptor_into_items(context, bpp_id, bpp_descriptor, i)
             for i in provider_items]
            [cast_price_and_rating_to_float(i) for i in provider_items]
            [cast_provider_category_fulfillment_id_to_string(i) for i in provider_items]
            [flatten_item_attributes(i) for i in provider_items]
            [enrich_item_type(i) for i in provider_items]
            provider_items = enrich_is_first_flag_for_items(provider_items)
            item_entries.extend(provider_items)
            new_p = {"offers": p.get("offers", [])}
            enrich_provider_details_into_items(p, new_p)
            enrich_context_bpp_id_and_descriptor_into_items(context, bpp_id, bpp_descriptor, new_p)
            provider_entries.append(new_p)

    [enrich_created_at_timestamp_in_item(i) for i in item_entries]
    [enrich_unique_id_in_item(i) for i in item_entries]
    return item_entries, provider_entries


def transform_item_into_product_attributes(item, attributes, variant_group_id):
    attrs, attr_values = [], []
    category = item["item_details"]["category_id"]
    for a in attributes:
        attr = ProductAttribute(**{"code": a["code"], "category": category, "domain": item["context"]["domain"],
                                   "provider": item["provider_details"]["id"],
                                   "timestamp": item["context"]["timestamp"],
                                   })
        attr_value = ProductAttributeValue(**{"product": item["id"], "category": category, "attribute_code": a["code"],
                                              "value": a["value"], "variant_group_id": variant_group_id,
                                              "provider": item["provider_details"]["id"],
                                              "timestamp": item["context"]["timestamp"],
                                              })
        attrs.append(attr)
        attr_values.append(attr_value)
    return attrs, attr_values


def transform_item_into_product_variant_group(org_id, local_id, variants, item):
    attrs = []
    for vl in variants:
        for v in vl:
            if v["code"] == "name":
                value_splits = v["value"].split(".")
                attrs.append(value_splits[-1])
    return VariantGroup(**{"local_id": local_id, "attribute_codes": attrs, "organisation": org_id,
                           "id": f"{org_id}_{local_id}",
                           "timestamp": item["context"]["timestamp"]})


def transform_item_into_custom_menu(org_id, local_id, custom_menu, item):
    return CustomMenu(**{"local_id": local_id, "parent_category_id": custom_menu.get("parent_category_id"),
                         "descriptor": custom_menu["descriptor"], "tags": custom_menu["tags"],
                         "id": f"{org_id}_{local_id}", "category": item["item_details"]["category_id"],
                         "domain": item["context"]["domain"], "provider": org_id,
                         "timestamp": item["context"]["timestamp"]})


def transform_item_into_customisation_group(org_id, local_id, custom_group, item):
    return CustomisationGroup(**{"local_id": local_id, "parent_category_id": custom_group.get("parent_category_id"),
                                 "descriptor": custom_group["descriptor"], "tags": custom_group["tags"],
                                 "id": f"{org_id}_{local_id}", "category": item["item_details"]["category_id"],
                                 "timestamp": item["context"]["timestamp"]})


def transform_item_categories(item):
    variant_groups, custom_menus, customisation_groups = [], [], []
    provider_id = item['provider_details']['id']
    categories = item["categories"]
    for c in categories:
        variants, variant_group_local_id = [], None
        local_id = c["id"]
        category_type = "variant_group"
        tags = c.get("tags", [])
        for t in tags:
            if t["code"] == "type":
                category_type = t["list"][0]["value"]
            if t["code"] == "attr":
                variants.append(t["list"])

        if category_type == "variant_group":
            for t in tags:
                if t["code"] == "attr":
                    variants.append(t["list"])
            if len(variants) > 0:
                variant_groups.append(transform_item_into_product_variant_group(provider_id, local_id, variants, item))
        elif category_type == "custom_menu":
            custom_menus.append(transform_item_into_custom_menu(provider_id, local_id, c, item))
        elif category_type == "custom_group":
            customisation_groups.append(transform_item_into_customisation_group(provider_id, local_id, c, item))

    return variant_groups, custom_menus, customisation_groups


def get_self_and_nested_customisation_group_id(item):
    customisation_group_id, customisation_nested_group_id = None, None
    tags = item["item_details"]["tags"]
    provider_id = item['provider_details']['id']
    for t in tags:
        if t["code"] == "parent":
            customisation_group_id = f'{provider_id}_{t["list"][0]["value"]}'
        if t["code"] == "child":
            customisation_nested_group_id = f'{provider_id}_{t["list"][0]["value"]}'

    return customisation_group_id, customisation_nested_group_id


def update_item_customisation_group_ids_with_children(existing_ids, items, all_ids=[]):
    new_ids = []
    for cid in existing_ids:
        for i in items:
            if i["type"] == "customization":
                tags = i['item_details'].get("tags", [])
                flag = False
                for t in tags:
                    if t["code"] == "parent":
                        flag = t["list"][0]["value"] == cid
                        if flag:
                            break

                if flag:
                    for t in tags:
                        if t["code"] == "child":
                            t_list = t["list"]
                            for l in t_list:
                                if l['value'] not in all_ids:
                                    new_ids.append(l['value'])

    all_ids += new_ids
    if len(new_ids) > 0:
        new_ids.extend(update_item_customisation_group_ids_with_children(list(set(new_ids)), items, all_ids))
    return new_ids


def update_location_with_serviceability(location, serviceabilities):
    if len(serviceabilities) > 0:
        serviceability = serviceabilities[0]
        try:
            location_type = "pan" if serviceability["type"] in ["11", "12"] else "polygon"
            location.__setattr__("type", location_type)

            if serviceability["unit"] == "polygon":
                val = json.loads(serviceability["val"])
                coordinates = val["features"][0]["geometry"]["coordinates"]
            elif serviceability["unit"] == "geojson":
                val = json.loads(serviceability["val"])
                multi_coordinates = val["features"][0]["geometry"]["coordinates"]
                coordinates = [x for xs in multi_coordinates for x in xs]
            elif serviceability["unit"] == "coordinates":
                val = json.loads(serviceability["val"])
                coordinates = [[[v['lat'], v['lng']] for v in val]]
            elif serviceability["unit"] == "km":
                coordinates = [create_simple_circle_polygon(location.gps[0], location.gps[1], float(serviceability["val"]))]
            else:
                return location

            location.__setattr__("polygons", {
                "type": "Polygon",
                "coordinates": coordinates
            })
        except JSONDecodeError:
            raise Exception("Serviceability JSON string parsing error")

    return location


def add_product_with_attributes(items, providers_with_offers, db_insert=True):
    products, final_attrs, final_attr_values, provider_categories = [], [], [], {}
    providers, locations, final_variant_groups, final_custom_menus, final_customisation_groups = [], [], [], [], []
    location_offers = []
    sub_categories = set()
    serviceabilities = dict()
    item_cg_ids = []
    domain = items[0]["context"]["domain"]

    for i in items:
        attributes, variants, variant_group_local_id = [], [], None
        item_details = i["item_details"]
        sub_categories.add(item_details["category_id"])
        tags = item_details["tags"]
        variant_groups, custom_menus, customisation_groups = transform_item_categories(i)

        provider_details = i["provider_details"]
        for t in provider_details["tags"]:
            if t["code"] == "serviceability":
                values = t["list"]
                serviceability = {}
                for v in values:
                    if v["code"] == "location":
                        serviceability["location"] = v["value"]
                    elif v["code"] == "type":
                        serviceability["type"] = v["value"]
                    elif v["code"] == "unit":
                        serviceability["unit"] = v["value"]
                    elif v["code"] == "val":
                        serviceability["val"] = v["value"]

                location_local_id = serviceability["location"]
                if location_local_id not in serviceabilities:
                    serviceabilities[location_local_id] = [serviceability]
                # else:
                #     serviceabilities[location_local_id].append(serviceability)

        # add categories in provider
        category = item_details["category_id"]
        provider_id = provider_details["id"]
        if provider_id in provider_categories:
            provider_categories[provider_id].add(category)
        else:
            provider_categories[provider_id] = {category}

        attr_codes = []
        for t in tags:
            if t["code"] == "attribute":
                attributes = t["list"]
            elif t["code"] == "custom_group":
                custom_group_list = t["list"]
                old_item_cg_ids = [c['value'] for c in custom_group_list]
                old_item_cg_ids.extend(update_item_customisation_group_ids_with_children(old_item_cg_ids, items, old_item_cg_ids))
                item_cg_ids = [f"{i['provider_details']['id']}_{cg}" for cg in old_item_cg_ids]

        custom_menu_configs = item_details.get("category_ids", [])
        custom_menu_new_list, variant_group_id = [], None
        for c in custom_menu_configs:
            [cm_id, item_rank] = c.split(":")
            cm = {"id": cm_id, "rank": item_rank}
            custom_menu_new_list.append(cm)

        custom_menu_new_list = sorted(custom_menu_new_list, key=lambda x: x["rank"])
        custom_menu_ids = [f"{i['provider_details']['id']}_{cm['id']}" for cm in custom_menu_new_list]
        i["custom_menus"] = custom_menu_ids

        if 'parent_item_id' in item_details and item_details['parent_item_id']:
            final_parent_item_id = f"{i['provider_details']['id']}_{item_details['parent_item_id']}"
            for v in variant_groups:
                if final_parent_item_id == v.id:
                    variant_group_id = v.id
                    attrs, attr_values = transform_item_into_product_attributes(i, attributes, final_parent_item_id)
                    attr_codes = [a.code for a in attrs]
                    final_attrs.extend(attrs)
                    final_attr_values.extend(attr_values)

        if len(customisation_groups) > 0 and i["type"] == "customization":
            i["customisation_group_id"], i["customisation_nested_group_id"] = get_self_and_nested_customisation_group_id(i)

        p = Product(**{"id": i["id"],
                       "product_code": item_details["descriptor"].get("code"),
                       "product_name": item_details["descriptor"].get("name"),
                       "category": item_details.get("category_id"),
                       "variant_group": variant_group_id,
                       "custom_menus": custom_menu_ids,
                       "customisation_groups": item_cg_ids,
                       "attribute_codes": attr_codes,
                       "timestamp": i["context"]["timestamp"],
                       })
        provider = Provider(**{"id": i['provider_details']['id'],
                               "local_id": i['provider_details']['local_id'],
                               "domain": i['context']['domain'],
                               "ttl": i['provider_details'].get('ttl'),
                               "descriptor": i['provider_details']['descriptor'],
                               "tags": i['provider_details'].get('tags'),
                               "time": i['provider_details'].get('time'),
                               "timestamp": i["context"]["timestamp"],
                               })
        if i['location_details'] and "id" in i['location_details']:
            coordinates_str = i['location_details'].get('gps', "0, 0").split(",")
            coordinates = [float(c) for c in coordinates_str]
            location = Location(**{"id": i['location_details']['id'],
                                   "local_id": i['location_details']['local_id'],
                                   "domain": i['context']['domain'],
                                   "provider": i['provider_details']['id'],
                                   "provider_descriptor": i['provider_details']['descriptor'],
                                   "gps": coordinates,
                                   "address": i['location_details'].get('address'),
                                   "circle": i['location_details'].get('circle'),
                                   "time": i['location_details'].get('time'),
                                   "timestamp": i["context"]["timestamp"],
                                   })
            location = update_location_with_serviceability(location, serviceabilities.get(i['location_details']['local_id'], []))
            locations.append(location)

        products.append(p)
        providers.append(provider)
        final_variant_groups = list({group.id: group for group in final_variant_groups}.values())
        final_variant_groups.extend(variant_groups)
        final_custom_menus = list({group.id: group for group in final_custom_menus}.values())
        final_custom_menus.extend(custom_menus)
        final_customisation_groups.extend(customisation_groups)
        final_customisation_groups = list({group.id: group for group in final_customisation_groups}.values())

    for pr in providers_with_offers:
        for o in pr["offers"]:
            for lo in o["location_ids"]:
                location_unique_id = f'{pr["provider_details"]["id"]}_{lo}'
                location_found = get_location_details_from_location_objects(locations, location_unique_id)
                location_offers.append(LocationOffer(**{
                    "id": f'{location_unique_id}_{o["id"]}',
                    "local_id": o['id'],
                    "domain": pr["context"]["domain"],
                    "provider": pr['provider_details']['id'],
                    "provider_descriptor": pr['provider_details']['descriptor'],
                    "descriptor": o["descriptor"],
                    "location": location_unique_id,
                    "item_ids": [f'{pr["provider_details"]["id"]}_{x}' for x in o["item_ids"]],
                    "time": o["time"],
                    "tags": o["tags"],
                    "type": location_found.type if location_found else "pan",
                    "polygons": location_found.polygons if location_found else None,
                    "timestamp": pr["context"]["timestamp"]
                    }))

    sub_category_objects = [SubCategory(**{"id": f"{domain}_{s}",
                                           "domain": domain,
                                           "name": s
                                           }) for s in sub_categories]
    providers = list({group.id: group for group in providers}.values())
    locations = list({l.id: l for l in locations}.values())
    final_custom_menus = list({l.id: l for l in final_custom_menus}.values())

    for p in providers:
        p.categories = list(provider_categories[p.id])
    for lo in locations:
        lo.categories = list(provider_categories.get(lo.provider, []))
    if db_insert:
        upsert_product_attributes(final_attrs)
        upsert_product_attribute_values(final_attr_values)
        upsert_variant_groups(final_variant_groups)
        upsert_custom_menus(final_custom_menus)
        upsert_customisation_groups(final_customisation_groups)
        upsert_products(products)
        upsert_providers(providers)
        upsert_locations(locations)
        upsert_location_offers(location_offers)
        upsert_sub_categories(sub_category_objects)
    return items


def add_product_with_attributes_incremental_flow(items):
    products, final_attrs, final_attr_values = [], [], []
    for i in items:
        attributes, variants, variant_group_local_id = [], [], None
        item_details = i["item_details"]
        tags = item_details["tags"]
        attr_codes = []
        for t in tags:
            if t["code"] == "attribute":
                attributes = t["list"]

        if 'parent_item_id' in item_details and item_details['parent_item_id']:
            final_parent_item_id = f"{i['provider_details']['id']}_{item_details['parent_item_id']}"
            attrs, attr_values = transform_item_into_product_attributes(i, attributes, final_parent_item_id)
            attr_codes = [a.code for a in attrs]
            final_attrs.extend(attrs)
            final_attr_values.extend(attr_values)

        if i["type"] == "customization":
            i["customisation_group_id"], i["customisation_nested_group_id"] = get_self_and_nested_customisation_group_id(i)

        p = {"id": i["id"],
             "product_code": item_details["descriptor"].get("code"),
             "product_name": item_details["descriptor"].get("name"),
             "category": item_details["category_id"],
             "attribute_codes": attr_codes,
             "timestamp": i["context"]["timestamp"]}

        products.append(p)

    upsert_product_attributes(final_attrs)
    upsert_product_attribute_values(final_attr_values)
    upsert_products_incremental_flow(products)
    return items


def upsert_product_attributes(product_attributes: List[ProductAttribute]):
    collection = get_mongo_collection('product_attribute')
    for p in product_attributes:
        filter_criteria = {"provider": p.provider, "code": p.code}
        p_dict = p.dict()
        p_dict["created_at"] = datetime.utcnow()
        mongo.collection_upsert_one(collection, filter_criteria, p_dict)


def upsert_product_attribute_values(product_attribute_values: List[ProductAttributeValue]):
    collection = get_mongo_collection('product_attribute_value')
    for p in product_attribute_values:
        filter_criteria = {"product": p.product, "attribute_code": p.attribute_code}
        p_dict = p.dict()
        p_dict["created_at"] = datetime.utcnow()
        mongo.collection_upsert_one(collection, filter_criteria, p_dict)


def upsert_variant_groups(variant_groups: List[VariantGroup]):
    collection = get_mongo_collection('variant_group')
    for v in variant_groups:
        filter_criteria = {"id": v.id}
        p_dict = v.dict()
        p_dict["created_at"] = datetime.utcnow()
        mongo.collection_upsert_one(collection, filter_criteria, p_dict)


def upsert_custom_menus(custom_menus: List[CustomMenu]):
    collection = get_mongo_collection('custom_menu')
    for v in custom_menus:
        filter_criteria = {"id": v.id}
        p_dict = v.dict()
        p_dict["created_at"] = datetime.utcnow()
        mongo.collection_upsert_one(collection, filter_criteria, p_dict)


def upsert_customisation_groups(customisation_groups: List[CustomisationGroup]):
    collection = get_mongo_collection('customisation_group')
    for v in customisation_groups:
        filter_criteria = {"id": v.id}
        p_dict = v.dict()
        p_dict["created_at"] = datetime.utcnow()
        mongo.collection_upsert_one(collection, filter_criteria, p_dict)


def upsert_products(products: List[Product]):
    collection = get_mongo_collection('product')
    for p in products:
        filter_criteria = {"id": p.id}
        p_dict = p.dict()
        p_dict["created_at"] = datetime.utcnow()
        mongo.collection_upsert_one(collection, filter_criteria, p_dict)


def upsert_products_incremental_flow(products: List[dict]):
    collection = get_mongo_collection('product')
    for p_dict in products:
        filter_criteria = {"id": p_dict["id"]}
        p_dict["created_at"] = datetime.utcnow()
        mongo.collection_upsert_one(collection, filter_criteria, p_dict)


def upsert_providers(products: List[Provider]):
    collection = get_mongo_collection('provider')
    for p in products:
        filter_criteria = {"id": p.id}
        old_p = mongo.collection_find_one(collection, filter_criteria) or {}
        p.categories = list(set(p.categories + old_p.get("categories", [])))
        p_dict = p.dict()
        p_dict["created_at"] = datetime.utcnow()
        mongo.collection_upsert_one(collection, filter_criteria, p_dict)


def upsert_providers_incremental_flow(products: List[dict]):
    collection = get_mongo_collection('provider')
    for p_dict in products:
        filter_criteria = {"id": p_dict["id"]}
        p_dict["created_at"] = datetime.utcnow()
        mongo.collection_upsert_one(collection, filter_criteria, p_dict)


def upsert_locations(locations: List[Location]):
    collection = get_mongo_collection('location')
    for p in locations:
        filter_criteria = {"id": p.id}
        old_p = mongo.collection_find_one(collection, filter_criteria) or {}
        p.categories = list(set(p.categories + old_p.get("categories", [])))
        p_dict = p.dict()
        p_dict["created_at"] = datetime.utcnow()
        mongo.collection_upsert_one(collection, filter_criteria, p_dict)


def upsert_locations_incremental_flow(locations: List[dict]):
    collection = get_mongo_collection('location')
    for p_dict in locations:
        filter_criteria = {"id": p_dict["id"]}
        p_dict["created_at"] = datetime.utcnow()
        mongo.collection_upsert_one(collection, filter_criteria, p_dict)


def upsert_location_offers(location_offers: List[LocationOffer]):
    collection = get_mongo_collection('location_offer')
    for p in location_offers:
        filter_criteria = {"id": p.id}
        p_dict = p.dict()
        p_dict["created_at"] = datetime.utcnow()
        mongo.collection_upsert_one(collection, filter_criteria, p_dict)


def upsert_sub_categories(sub_categories: List[SubCategory]):
    collection = get_mongo_collection('sub_category')
    for p in sub_categories:
        filter_criteria = {"id": p.id}
        p_dict = p.dict()
        p_dict["created_at"] = datetime.utcnow()
        mongo.collection_upsert_one(collection, filter_criteria, p_dict)


@check_for_exception
def add_search_catalogues(bpp_response):
    log(f"Adding search catalogs with message-id: {bpp_response['context']['message_id']} for {bpp_response['context']['bpp_id']}")
    context = bpp_response[constant.CONTEXT]
    if constant.MESSAGE not in bpp_response:
        return get_ack_response(context=context, ack=False, error=RegistryLookupError.REGISTRY_ERROR.value)

    catalog = bpp_response[constant.MESSAGE][constant.CATALOG]
    items, providers = flatten_catalog_into_item_entries(catalog, context)

    if len(items) == 0:
        return get_ack_response(context=context, ack=True)
    search_collection = get_mongo_collection('on_search_items')
    is_successful = True

    items = add_product_with_attributes(items, providers)
    for i in items:
        # Upsert a single document
        i["timestamp"] = i["context"]["timestamp"]
        i["created_at"] = datetime.utcnow()
        filter_criteria = {"id": i['id']}
        is_successful = is_successful and mongo.collection_upsert_one(search_collection, filter_criteria, i)

    if is_successful:
        log(f"Search catalogs added successfully, message-id: {bpp_response['context']['message_id']} for {bpp_response['context']['bpp_id']}")
        return get_ack_response(context=context, ack=True)
    else:
        log(f"Search catalogs failed while adding, message-id: {bpp_response['context']['message_id']} for {bpp_response['context']['bpp_id']}")
        return get_ack_response(context=context, ack=False, error=DatabaseError.ON_WRITE_ERROR.value)


def add_search_catalogues_for_test(bpp_response):
    log(f"Adding search catalogs(for test) with message-id: {bpp_response['context']['message_id']} for {bpp_response['context']['bpp_id']}")
    context = bpp_response[constant.CONTEXT]
    if constant.MESSAGE not in bpp_response:
        return get_ack_response(context=context, ack=False, error=RegistryLookupError.REGISTRY_ERROR.value)
    catalog = bpp_response[constant.MESSAGE][constant.CATALOG]
    items, providers = flatten_catalog_into_item_entries(catalog, context)

    if len(items) == 0:
        return get_ack_response(context=context, ack=True)

    add_product_with_attributes(items, providers, db_insert=False)
    return get_ack_response(context=context, ack=True)


@check_for_exception
def add_incremental_search_catalogues(bpp_response):
    log(f"Adding incremental search catalogs with message-id: {bpp_response['context']['message_id']} for {bpp_response['context']['bpp_id']}")
    catalog = bpp_response[constant.MESSAGE][constant.CATALOG]
    bpp_providers = catalog.get(constant.BPP_PROVIDERS, [])
    bpp_provider_first = bpp_providers[0]
    if "items" in bpp_provider_first:
        return add_incremental_search_catalogues_for_items_update(bpp_response)
    elif "locations" in bpp_provider_first:
        return add_incremental_search_catalogues_for_locations_update(bpp_response)
    else:
        return add_incremental_search_catalogues_for_provider_update(bpp_response)


def get_similar_existing_item(item_id, provider_id, location_id, item_type):
    item = get_on_search_item_for_given_id(item_id)
    if not item:
        item = get_on_search_item_for_given_details(provider_id, location_id, item_type)
    return item


def add_incremental_search_catalogues_for_items_update(bpp_response):
    context = bpp_response[constant.CONTEXT]
    log(f"Adding incremental search catalog (item) update for {context['bpp_id']}")
    if constant.MESSAGE not in bpp_response:
        return get_ack_response(context=context, ack=False, error=RegistryLookupError.REGISTRY_ERROR.value)
    catalog = bpp_response[constant.MESSAGE][constant.CATALOG]
    items, _ = flatten_catalog_into_item_entries(catalog, context)

    if len(items) == 0:
        return get_ack_response(context=context, ack=True)
    search_collection = get_mongo_collection('on_search_items')

    items = add_product_with_attributes_incremental_flow(items)
    for i in items:
        similar_existing_item = get_similar_existing_item(i["id"], i['provider_details']['id'],
                                                          i['item_details']['location_id'], i['type'])
        new_i = similar_existing_item.copy()
        new_i.update(project(i, ["id", "local_id", "item_details", "attributes", "is_first", "type",
                                 "customisation_group_id", "customisation_nested_group_id", "context"]))

        # Upsert a single document
        filter_criteria = {"id": i["id"]}
        new_i["created_at"] = datetime.utcnow()
        new_i["timestamp"] = i["context"]["timestamp"]
        mongo.collection_upsert_one(search_collection, filter_criteria, new_i)

    return get_ack_response(context=context, ack=True)


def add_incremental_search_catalogues_for_locations_update(bpp_response):
    context = bpp_response[constant.CONTEXT]
    mongo_collection = get_mongo_collection('location')
    catalog = bpp_response[constant.MESSAGE][constant.CATALOG]
    bpp_providers = catalog.get(constant.BPP_PROVIDERS, [])
    for p in bpp_providers:
        locations = p["locations"]
        for l in locations:
            l["id"] = f"{context[constant.BPP_ID]}_{context[constant.DOMAIN]}_{p['id']}_{l['id']}"
            l["timestamp"] = context["timestamp"]
            l["created_at"] = datetime.utcnow()
            if check_if_entity_present_for_given_id("location", l["id"]):
                filter_criteria = {"id": l['id']}
                mongo.collection_upsert_one(mongo_collection, filter_criteria, l)
            else:
                return get_ack_response(context=context, ack=False, error={
                    "code": "UNKNOWN",
                    "message": "Location-id not available from full catalog!",
                }), 400

    return get_ack_response(context=context, ack=True)


def add_incremental_search_catalogues_for_provider_update(bpp_response):
    context = bpp_response[constant.CONTEXT]
    mongo_collection = get_mongo_collection('provider')
    catalog = bpp_response[constant.MESSAGE][constant.CATALOG]
    bpp_providers = catalog.get(constant.BPP_PROVIDERS, [])
    for p in bpp_providers:
        p["id"] = f"{context[constant.BPP_ID]}_{context[constant.DOMAIN]}_{p['id']}"
        p["timestamp"] = context["timestamp"]
        p["created_at"] = datetime.utcnow()
        if check_if_entity_present_for_given_id("provider", p["id"]):
            filter_criteria = {"id": p['id']}
            mongo.collection_upsert_one(mongo_collection, filter_criteria, p)
        else:
            return get_ack_response(context=context, ack=False, error={
                "code": "UNKNOWN",
                "message": "Provider-id not available from full catalog!",
            }), 400

    return get_ack_response(context=context, ack=True)


@MeasureTime
def gateway_search(search_request, headers={}):
    request_type = 'search'
    gateway_url = fetch_subscriber_url_from_lookup(request_type, domain=search_request['context']['domain'])
    search_url = f"{gateway_url}{request_type}" if gateway_url.endswith("/") else f"{gateway_url}/{request_type}"
    auth_header = create_authorisation_header(search_request)
    log(f"making request to bg or bpp with {search_request}")
    headers.update({'Authorization': auth_header})
    return post_on_bg_or_bpp(search_url, payload=search_request, headers=headers)


def get_query_object(**kwargs):
    query_object = {"type": "item", "is_first": True}
    if kwargs['price_min'] and kwargs['price_max']:
        query_object.update({'item_details.price.value': {'$gte': kwargs['price_min'], '$lte': kwargs['price_max']}})
    elif kwargs['price_min']:
        query_object.update({'item_details.price.value': {'$gte': kwargs['price_min']}})
    elif kwargs['price_max']:
        query_object.update({'item_details.price.value': {'$lte': kwargs['price_max']}})

    if kwargs['name']:
        query_object.update({'item_details.descriptor.name': re.compile(kwargs["name"], re.IGNORECASE)})
    if kwargs['custom_menu']:
        query_object.update({'custom_menus': kwargs['custom_menu']})
    if kwargs['sub_category']:
        query_object.update({'item_details.category_id': kwargs['sub_category']})
    if kwargs['rating']:
        query_object.update({'item_details.rating.value': {'$gte': kwargs['rating']}})
    if kwargs['provider_ids']:
        query_object.update({'provider_details.id': {'$in': [x.strip() for x in kwargs['provider_ids']]}})
    if kwargs['location_ids']:
        query_object.update({'location_details.id': {'$in': [x.strip() for x in kwargs['location_ids']]}})
    if kwargs['category_ids']:
        query_object.update({'item_details.category_id': {'$in': [x.strip() for x in kwargs['category_ids']]}})
    if kwargs['fulfillment_ids']:
        query_object.update({'item_details.fulfillment_id': {'$in': [x.strip() for x in kwargs['fulfillment_ids']]}})
    if kwargs['product_attrs'] and len(kwargs['product_attrs']) > 0:
        for k, v in kwargs['product_attrs'].items():
            query_object.update({f'attributes.{k}': {'$in': [x.strip() for x in v]}})
    return query_object


def get_sort_field_and_order(**kwargs):
    if kwargs['sort_field'] == 'price':
        sort_field = 'price.value'
    elif kwargs['sort_field'] == 'rating':
        sort_field = 'rating.value'
    else:
        sort_field = None
    sort_order = pymongo.ASCENDING if kwargs['sort_order'] == 'asc' else pymongo.DESCENDING
    return sort_field, sort_order


def get_item_catalogues(**kwargs):
    search_collection = get_mongo_collection('on_search_items')
    query_object = get_query_object(**kwargs)
    sort_field, sort_order = get_sort_field_and_order(**kwargs)
    page_number = kwargs['page_number'] - 1
    limit = kwargs['limit']
    skip = page_number * limit
    catalogs = mongo.collection_find_all(search_collection, query_object, sort_field, sort_order,
                                         skip=skip, limit=limit)
    if catalogs:
        # items = catalogs['data']
        # catalogs['data'] = [cast_price_and_rating_to_string(i) for i in items]
        return catalogs
    else:
        return {"error": DatabaseError.ON_READ_ERROR.value}


def get_filters_out_of_items(items):
    category_values = [i[constant.CATEGORY_DETAILS] for i in items if 'id' in i[constant.CATEGORY_DETAILS]]
    fulfillment_values = [i[constant.FULFILLMENT_DETAILS] for i in items if 'id' in i[constant.FULFILLMENT_DETAILS]]
    provider_values = [i[constant.PROVIDER_DETAILS] for i in items if 'id' in i[constant.PROVIDER_DETAILS]]
    price_values = [i[constant.ITEM_DETAILS][constant.PRICE]['value'] for i in items]

    categories = list({v['id']: {'id': v['id'], 'name': v.get('descriptor', {}).get('name')}
                       for v in category_values}.values())
    fulfillment = list({v['id']: {'id': v['id'], 'name': v.get('descriptor', {}).get('name')}
                        for v in fulfillment_values}.values())
    providers = list({v['id']: {'id': v['id'], 'name': v.get('descriptor', {}).get('name')}
                      for v in provider_values}.values())
    min_price = min(price_values)
    max_price = max(price_values)
    return {
        "categories": categories,
        "fulfillment": fulfillment,
        "providers": providers,
        "minPrice": min_price,
        "maxPrice": max_price,
    }


def check_for_quantity_in_items(items):
    flag = True
    for i in items:
        flag = flag and ("quantity" in i) and ('available' in i['quantity']) and ('maximum' in i['quantity'])
    return flag


def get_item_details(item_id):
    search_collection = get_mongo_collection("on_search_items")
    product_collection = get_mongo_collection("product")
    variant_group_collection = get_mongo_collection("variant_group")
    attr_value_collection = get_mongo_collection("product_attribute_value")
    customisation_group_collection = get_mongo_collection("customisation_group")
    on_search_item = mongo.collection_find_one(search_collection, {"id": item_id})
    product_details = mongo.collection_find_one(product_collection, {"id": item_id})
    variant_group_id = product_details.get("variant_group")
    if variant_group_id:
        variant_group = mongo.collection_find_one(variant_group_collection, {"id": variant_group_id})
        variant_attrs = variant_group["attribute_codes"]
        variant_value_list = mongo.collection_find_all(attr_value_collection, {"variant_group_id": variant_group_id,
                                                                               "attribute_code": {'$in': variant_attrs}},
                                                       limit=None)["data"]
        on_search_item["variant_attr_values"] = variant_value_list

    # Customisation Group and Items
    customisation_group_ids = product_details.get("customisation_groups", [])
    customisation_groups = mongo.collection_find_all(customisation_group_collection,
                                                     {"id": {'$in': customisation_group_ids}})["data"]
    customisation_items = mongo.collection_find_all(search_collection,
                                                    {"context.bpp_id": on_search_item["context"]["bpp_id"],
                                                     # "provider_details.id": on_search_item["provider_details"]["id"],
                                                     "type": "customization",
                                                     "customisation_group_id": {'$in': customisation_group_ids}},
                                                    limit=None)["data"]
    on_search_item["customisation_groups"] = customisation_groups
    on_search_item["customisation_items"] = customisation_items

    # Related Products
    if variant_group_id:
        related_products = mongo.collection_find_all(product_collection, {"variant_group": variant_group_id})["data"]
        related_product_ids = [r["id"] for r in related_products]
        related_products_with_details = mongo.collection_find_all(search_collection,
                                                                  {"id": {'$in': [x.strip() for x in related_product_ids]}})["data"]
        on_search_item["related_items"] = related_products_with_details
    else:
        on_search_item["related_items"] = []
    return on_search_item


def get_custom_menus(**kwargs):
    mongo_collection = get_mongo_collection("custom_menu")
    query_object = {k: v for k, v in kwargs.items() if v is not None}
    custom_menus = mongo.collection_find_all(mongo_collection, query_object)
    return custom_menus


def get_providers(**kwargs):
    mongo_collection = get_mongo_collection("provider")
    query_object = {k: v for k, v in kwargs.items() if v is not None}
    providers = mongo.collection_find_all(mongo_collection, query_object)
    return providers


def get_locations(**kwargs):
    mongo_collection = get_mongo_collection("location")
    lat = kwargs.pop("latitude", None)
    long = kwargs.pop("longitude", None)
    query_object = {k: v for k, v in kwargs.items() if v is not None}
    if lat and long:
        query_object.update(
            {"$or": [
                {"polygons":
                     {"$geoIntersects":
                          {"$geometry": {"type": "Point", "coordinates": [lat, long]}}
                      }
                 },
                {"type": "pan"}]
            }
        )
    providers = mongo.collection_find_all(mongo_collection, query_object, geo_spatial=True)
    for p in providers["data"]:
        p.pop("polygons")
    return providers


def get_location_offers(**kwargs):
    mongo_collection = get_mongo_collection("location_offer")
    lat = kwargs.pop("latitude", None)
    long = kwargs.pop("longitude", None)
    query_object = {k: v for k, v in kwargs.items() if v is not None}
    if lat and long:
        query_object.update(
            {"$or": [
                {"polygons":
                     {"$geoIntersects":
                          {"$geometry": {"type": "Point", "coordinates": [lat, long]}}
                      }
                 },
                {"type": "pan"}]
            }
        )
    providers = mongo.collection_find_all(mongo_collection, query_object, geo_spatial=True)
    for p in providers["data"]:
        p.pop("polygons")
    return providers


def get_item_attributes(**kwargs):
    mongo_collection = get_mongo_collection("product_attribute")
    query_object = {k: v for k, v in kwargs.items() if v is not None}
    item_attributes = mongo.collection_find_all(mongo_collection, query_object, limit=None)
    return item_attributes


def get_item_attribute_values(**kwargs):
    mongo_collection = get_mongo_collection("product_attribute_value")
    query_object = {k: v for k, v in kwargs.items() if v is not None}
    item_attribute_values = mongo.collection_find_distinct(mongo_collection, query_object, distinct="value")
    return item_attribute_values


@check_for_exception
def get_custom_menu_details(custom_menu_id):
    mongo_collection = get_mongo_collection("custom_menu")
    custom_menu = mongo.collection_find_one(mongo_collection, {"id": custom_menu_id})
    return custom_menu


@check_for_exception
def get_provider_details(provider_id):
    mongo_collection = get_mongo_collection("provider")
    custom_menu = mongo.collection_find_one(mongo_collection, {"id": provider_id})
    return custom_menu


@check_for_exception
def get_location_details(location_id):
    mongo_collection = get_mongo_collection("location")
    custom_menu = mongo.collection_find_one(mongo_collection, {"id": location_id})
    return custom_menu


def dump_on_search_payload(payload):
    collection = get_mongo_collection('on_search_dump')
    payload["created_at"] = datetime.utcnow()
    payload["status"] = "PENDING"
    return mongo.collection_insert_one(collection, payload)


def update_on_search_dump_status(object_id, status, response_time=None):
    collection = get_mongo_collection('on_search_dump')
    filter_criteria = {"_id": object_id}
    value = {"status": status}
    if response_time:
        value["response_time"] = response_time
    collection.update_one(filter_criteria, {'$set': value})


def get_last_search_dump_timestamp(transaction_id):
    search_collection = get_mongo_collection('request_dump')
    query_object = {"action": "search", "request.context.transaction_id": transaction_id}
    catalog = mongo.collection_find_one_with_sort(search_collection, query_object, "created_at")
    return catalog['created_at'] if catalog else None


def get_last_request_dump(request_type, transaction_id):
    search_collection = get_mongo_collection('request_dump')
    query_object = {"action": request_type, "request.context.transaction_id": transaction_id}
    catalog = mongo.collection_find_one_with_sort(search_collection, query_object, "created_at")
    if catalog:
        catalog.pop("created_at")
        return catalog
    else:
        return {"error": "No request found for given type and transaction_id!"}, 400


def get_categories():
    return [
        {"domain": "ONDC:RET10", "name": "Grocery"},
        {"domain": "ONDC:RET11", "name": "F&B"},
        {"domain": "ONDC:RET12", "name": "Fashion"},
        {"domain": "ONDC:RET13", "name": "BPC"},
        {"domain": "ONDC:RET14", "name": "Electronics"},
        {"domain": "ONDC:RET15", "name": "Appliances"},
        {"domain": "ONDC:RET16", "name": "Home & Kitchen"},
        {"domain": "ONDC:RET17", "name": "RET17"},
        {"domain": "ONDC:RET18", "name": "Health & Wellness"},
        {"domain": "ONDC:RET19", "name": "Pharma"},
        {"domain": "ONDC:RET20", "name": "RET20"},
        {"domain": "ONDC:AGR10", "name": "Agriculture"}
    ]


def get_sub_categories(domain):
    mongo_collection = get_mongo_collection("sub_category")
    query_object = {"domain": domain}
    sub_categories = mongo.collection_find_all(mongo_collection, query_object)
    return sub_categories
