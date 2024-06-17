from datetime import datetime
from enum import Enum
from typing import Optional, Union, List
from uuid import UUID

from pydantic import BaseModel, validator, ValidationError

from validations.schema_validations.retail.models.schema import Context, Catalog, Error, Order, Descriptor, Issue, Provider, \
    Location, Item, AddOn, Offer, Quotation, Billing, Fulfillment, Payment, RatingMessage, Tracking, OnRatingMessage, \
    Domain, CodeModel, Code, Action, IncrCatalog


class Status(Enum):
    ACK = 'ACK'
    NACK = 'NACK'


class SearchMessage(BaseModel):
    intent: dict


class OrderMessage(BaseModel):
    order: Order


class StatusMessage(BaseModel):
    order_id: Union[float, str]


class TrackMessage(BaseModel):
    order_id: Union[float, str]
    callback_url: Optional[str]


class CancelMessage(BaseModel):
    order_id: Union[float, str]
    cancellation_reason_id: Optional[Union[float, str]]
    descriptor: Optional[Descriptor]


class UpdateMessage(BaseModel):
    order: Order
    update_target: str


class SupportMessage(BaseModel):
    ref_id: str


class IssueMessage(BaseModel):
    issue: Issue

    @validator("issue")
    def validate_value(cls, v, values):
        """Validate each item"""
        if v.id is None:
            raise ValidationError("Issue id is missing!")
        return v


class IssueStatusMessage(BaseModel):
    issue_id: UUID


class OnCallContext(BaseModel):
    domain: Domain
    country: CodeModel
    city: Code
    action: Action
    core_version: str
    bap_id: str
    bap_uri: str
    bpp_id: str
    bpp_uri: str
    transaction_id: str
    message_id: str
    timestamp: datetime
    key: Optional[str]
    ttl: Optional[Union[str, int]]


class OnSearchMessage(BaseModel):
    catalog: Optional[Catalog]


class IncrOnSearchMessage(BaseModel):
    catalog: Optional[IncrCatalog]


class OnSelectOrder(BaseModel):
    provider: Optional[Provider]
    provider_location: Optional[Location]
    items: Optional[List[Item]]
    add_ons: Optional[List[AddOn]]
    offers: Optional[List[Offer]]
    quote: Optional[Quotation]


class OnSelectMessage(BaseModel):
    order: OnSelectOrder


class OnInitOrder(BaseModel):
    provider: Optional[Provider]
    provider_location: Optional[Location]
    items: Optional[List[Item]]
    add_ons: Optional[List[AddOn]]
    offers: Optional[List[Offer]]
    quote: Quotation
    billing: Optional[Billing]
    fulfillment: Optional[Fulfillment]
    payment: Optional[Payment]


class OnInitMessage(BaseModel):
    order: OnInitOrder


class OnTrackMessage(BaseModel):
    tracking: Tracking


class OnSupportMessage(BaseModel):
    phone: Optional[str]
    email: Optional[str]
    uri: Optional[str]


class OnIssueMessage(BaseModel):
    issue: Issue

    @validator("issue")
    def validate_value(cls, v, values):
        """Validate each item"""
        if v.id is None:
            raise ValidationError("Issue id is missing!")
        return v


class OnIssueStatusMessage(BaseModel):
    issue: Issue

    @validator("issue")
    def validate_value(cls, v, values):
        """Validate each item"""
        if v.order_details is None:
            raise ValidationError("Issue order_details is missing!")
        return v


class SearchRequest(BaseModel):
    context: Context
    message: SearchMessage
    error: Optional[Error]


class SelectRequest(BaseModel):
    context: Context
    message: OrderMessage
    error: Optional[Error]


class InitRequest(BaseModel):
    context: Context
    message: OrderMessage
    error: Optional[Error]


class ConfirmRequest(BaseModel):
    context: Context
    message: OrderMessage
    error: Optional[Error]


class StatusRequest(BaseModel):
    context: Context
    message: StatusMessage
    error: Optional[Error]


class TrackRequest(BaseModel):
    context: Context
    message: TrackMessage
    error: Optional[Error]


class CancelRequest(BaseModel):
    context: Context
    message: CancelMessage
    error: Optional[Error]


class UpdateRequest(BaseModel):
    context: Context
    message: UpdateMessage
    error: Optional[Error]


class RatingRequest(BaseModel):
    context: Context
    message: RatingMessage
    error: Optional[Error]


class SupportRequest(BaseModel):
    context: Context
    message: SupportMessage
    error: Optional[Error]


class IssueRequest(BaseModel):
    context: Context
    message: IssueMessage
    error: Optional[Error]


class IssueStatusRequest(BaseModel):
    context: Context
    message: IssueStatusMessage
    error: Optional[Error]


class FullOnSearchRequest(BaseModel):
    context: OnCallContext
    message: OnSearchMessage
    error: Optional[Error]

    @validator("message")
    def validate_catalog(cls, v, values):
        if v.catalog is None:
            raise ValidationError("Catalog is missing!")
        return v


class IncrOnSearchRequest(BaseModel):
    context: OnCallContext
    message: IncrOnSearchMessage
    error: Optional[Error]

    @validator("message")
    def validate_catalog(cls, v, values):
        if v.catalog is None:
            raise ValidationError("Catalog is missing!")
        return v


class OnSelectRequest(BaseModel):
    context: OnCallContext
    message: OnSelectMessage
    error: Optional[Error]


class OnInitRequest(BaseModel):
    context: OnCallContext
    message: OnInitMessage
    error: Optional[Error]


class OnConfirmRequest(BaseModel):
    context: OnCallContext
    message: OrderMessage
    error: Optional[Error]


class OnStatusRequest(BaseModel):
    context: OnCallContext
    message: OrderMessage
    error: Optional[Error]


class OnTrackRequest(BaseModel):
    context: OnCallContext
    message: OnTrackMessage
    error: Optional[Error]


class OnCancelRequest(BaseModel):
    context: OnCallContext
    message: OrderMessage
    error: Optional[Error]


class OnUpdateRequest(BaseModel):
    context: OnCallContext
    message: OrderMessage
    error: Optional[Error]


class OnRatingRequest(BaseModel):
    context: OnCallContext
    message: OnRatingMessage
    error: Optional[Error]


class OnSupportRequest(BaseModel):
    context: OnCallContext
    message: OnSupportMessage
    error: Optional[Error]


class OnIssueRequest(BaseModel):
    context: OnCallContext
    message: OnIssueMessage
    error: Optional[Error]


class OnIssueStatusRequest(BaseModel):
    context: OnCallContext
    message: dict
    error: Optional[Error]
