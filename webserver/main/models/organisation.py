from datetime import time

from pydantic import BaseModel, Field
from typing import Dict, Optional


class BankDetails(BaseModel):
    acc_holder_name: str
    acc_number: str
    ifsc: str
    cancelled_cheque: str
    bank_name: str
    branch_name: str


class PAN(BaseModel):
    pan: str
    proof: str


class GSTN(BaseModel):
    gstn: str
    proof: str


class Location(BaseModel):
    lat: float
    long: float


class Address(BaseModel):
    building: str
    city: str
    state: str
    country: str
    area_code: str
    locality: str


class SupportDetails(BaseModel):
    email: str
    mobile: str


class StoreTiming(BaseModel):
    # Define the fields for store timing as per your requirements
    pass


class Radius(BaseModel):
    # Define the fields for radius as per your requirements
    pass


class StoreDetails(BaseModel):
    categories: Dict
    logo: str
    location: Location
    location_availability_pan_india: bool
    city: Dict
    default_cancellable: bool
    default_returnable: bool
    address: Address
    support_details: SupportDetails
    store_timing: StoreTiming
    radius: Radius
    logistics_bpp_id: str


class Organization(BaseModel):
    id: str
    name: str
    address: Optional[str]
    contact_email: Optional[str]
    contact_mobile: Optional[str]
    address_proof: Optional[str]
    id_proof: Optional[str]
    bank_details: Optional[BankDetails]
    pan: Optional[PAN]
    gstn: Optional[GSTN]
    fssai: Optional[str]
    created_at: int = Field(default_factory=lambda: int(time.time() * 1000))
    store_details: StoreDetails
    created_by: Optional[str]
