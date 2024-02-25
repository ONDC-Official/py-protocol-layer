from typing import Optional, List
from pydantic import BaseModel
from enum import Enum


class SearchType(Enum):
    FULL = "full"
    INC = "inc"


class Product(BaseModel):
    id: str
    product_code: Optional[str]
    product_name: str
    variant_group: Optional[str]
    custom_menus: Optional[List[str]]
    customisation_groups: List[str]
    attribute_codes: list
    category: Optional[str]
    sub_category1: Optional[str]
    sub_category2: Optional[str]
    sub_category3: Optional[str]
    timestamp: str


class ProductAttribute(BaseModel):
    code: str
    category: str
    domain: str
    provider: str
    sub_category1: Optional[str]
    sub_category2: Optional[str]
    sub_category3: Optional[str]
    timestamp: str


class ProductAttributeValue(BaseModel):
    product: str
    category: str
    attribute_code: str
    provider: str
    value: str
    variant_group_id: Optional[str]
    timestamp: str


class VariantGroup(BaseModel):
    id: str
    local_id: str
    organisation: str
    attribute_codes: list
    timestamp: str


class CustomMenu(BaseModel):
    id: str
    local_id: str
    domain: str
    provider: str
    category: str
    parent_category_id: Optional[str]
    descriptor: dict
    tags: List[dict]
    timestamp: str


class CustomisationGroup(BaseModel):
    id: str
    local_id: str
    category: str
    parent_category_id: Optional[str]
    descriptor: dict
    tags: List[dict]
    timestamp: str


class Provider(BaseModel):
    id: str
    local_id: str
    domain: str
    descriptor: dict
    ttl: Optional[str]
    tags: Optional[List[dict]]
    time: Optional[dict]
    categories: Optional[list]
    timestamp: str


class Location(BaseModel):
    id: str
    local_id: str
    domain: str
    provider: str
    provider_descriptor: dict
    gps: list
    type: Optional[str]
    polygons: Optional[dict]
    address: Optional[dict]
    circle: Optional[dict]
    time: Optional[dict]
    categories: Optional[list]
    timestamp: str


class LocationOffer(BaseModel):
    id: str
    local_id: str
    domain: str
    provider: str
    provider_descriptor: dict
    descriptor: dict
    location: str
    item_ids: List[str]
    time: Optional[dict]
    tags: Optional[list]
    polygons: Optional[dict]
    timestamp: str
