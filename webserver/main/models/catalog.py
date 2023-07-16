from typing import Optional

from pydantic import BaseModel


class Product(BaseModel):
    id: str
    product_code: str
    product_name: str
    variant_group: str
    attribute_codes: list
    mrp: Optional[float]
    retail_price: Optional[float]
    purchase_price: Optional[float]
    retail_price: Optional[float]
    hsn_code: Optional[str]
    gst_percentage: Optional[float]
    product_category: Optional[str]
    product_subcategory1: Optional[str]
    product_subcategory2: Optional[str]
    product_subcategory3: Optional[str]
    quantity: Optional[float]
    barcode: Optional[int]
    max_allowed_quantity: Optional[float]
    package_quantity: Optional[str]
    unit_of_measure: Optional[str]
    length: Optional[str]
    breadth: Optional[str]
    height: Optional[str]
    weight: Optional[str]
    is_returnable: Optional[bool]
    return_window: Optional[str]
    is_vegetarian: Optional[bool]
    manufacturer_name: Optional[str]
    manufactured_date: Optional[str]
    nutritional_info: Optional[str]
    additive_info: Optional[str]
    instructions: Optional[str]
    is_cancellable: Optional[bool]
    available_on_cod: Optional[bool]
    long_description: Optional[str]
    description: Optional[str]
    organization: Optional[str]
    images: Optional[list]
    createdBy: Optional[str]
    published: bool = True
    manufacturer_or_packer_name: Optional[str]
    manufacturer_or_packer_address: Optional[str]
    common_or_generic_name_of_commodity: Optional[str]
    month_year_of_manufacture_packing_import: Optional[str]
    importer_fssai_license_no: Optional[str]
    brand_owner_fssai_license_no: Optional[str]


class ProductAttribute(BaseModel):
    code: str
    created_by: Optional[str]
    updated_by: Optional[str]
    created_at: Optional[int]
    updated_at: Optional[int]


class ProductAttributeValue(BaseModel):
    product: str
    attribute_code: str
    value: str
    created_by: Optional[str]
    updated_by: Optional[str]
    created_at: Optional[int]
    updated_at: Optional[int]


# class VariantType(BaseModel):
#     id: str
#     organisation: str
#     name: str
#     category: str
#     sub_category: str
#     created_by: str
#     updated_by: str
#     created_at: int
#     updated_at: int
#
#
# class VariantValue(BaseModel):
#     id: str
#     organisation: str
#     variant_type: str
#     value: str
#     product: str
#     created_by: str
#     updated_by: str
#     created_at: int
#     updated_at: int


class VariantGroup(BaseModel):
    id: str
    local_id: str
    organisation: str
    attribute_codes: list
    created_at: Optional[int]
    updated_at: Optional[int]
