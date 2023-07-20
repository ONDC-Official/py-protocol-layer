from typing import Optional

from pydantic import BaseModel


class Product(BaseModel):
    id: str
    product_code: str
    product_name: str
    variant_group: str
    attribute_codes: list
    category: str
    sub_category1: Optional[str]
    sub_category2: Optional[str]
    sub_category3: Optional[str]


class ProductAttribute(BaseModel):
    code: str
    category: str
    sub_category1: Optional[str]
    sub_category2: Optional[str]
    sub_category3: Optional[str]


class ProductAttributeValue(BaseModel):
    product: str
    attribute_code: str
    value: str


class VariantGroup(BaseModel):
    id: str
    local_id: str
    organisation: str
    attribute_codes: list
