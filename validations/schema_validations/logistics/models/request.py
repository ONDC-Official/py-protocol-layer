from enum import Enum
from typing import Optional, Union, List
from uuid import UUID

from pydantic import BaseModel, validator, ValidationError

from validations.schema_validations.logistics.models.schema import Catalog, Error, Order, Descriptor, Issue, Provider, \
    Location, Item, AddOn, Offer, Quotation, Billing, Fulfillment, Payment, Tracking


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
    id: UUID


class OnSearchMessage(BaseModel):
    catalog: Optional[Catalog]


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
    quote: Optional[Quotation]
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
    context: dict
    message: dict
    error: Optional[Error]


class SelectRequest(BaseModel):
    context: dict
    message: dict
    error: Optional[Error]


class InitRequest(BaseModel):
    context: dict
    message: dict
    error: Optional[Error]


class ConfirmRequest(BaseModel):
    context: dict
    message: dict
    error: Optional[Error]


class StatusRequest(BaseModel):
    context: dict
    message: dict
    error: Optional[Error]


class TrackRequest(BaseModel):
    context: dict
    message: dict
    error: Optional[Error]


class CancelRequest(BaseModel):
    context: dict
    message: dict
    error: Optional[Error]


class UpdateRequest(BaseModel):
    context: dict
    message: dict
    error: Optional[Error]


class RatingRequest(BaseModel):
    context: dict
    message: dict
    error: Optional[Error]


class SupportRequest(BaseModel):
    context: dict
    message: dict
    error: Optional[Error]


class IssueRequest(BaseModel):
    context: dict
    message: dict
    error: Optional[Error]


class IssueStatusRequest(BaseModel):
    context: dict
    message: dict
    error: Optional[Error]


class OnSearchRequest(BaseModel):
    context: dict
    message: dict
    error: Optional[Error]


class OnSelectRequest(BaseModel):
    context: dict
    message: dict
    error: Optional[Error]


class OnInitRequest(BaseModel):
    context: dict
    message: dict
    error: Optional[Error]


class OnConfirmRequest(BaseModel):
    context: dict
    message: dict
    error: Optional[Error]


class OnStatusRequest(BaseModel):
    context: dict
    message: dict
    error: Optional[Error]


class OnTrackRequest(BaseModel):
    context: dict
    message: dict
    error: Optional[Error]


class OnCancelRequest(BaseModel):
    context: dict
    message: dict
    error: Optional[Error]


class OnUpdateRequest(BaseModel):
    context: dict
    message: dict
    error: Optional[Error]


class OnRatingRequest(BaseModel):
    context: dict
    message: dict
    error: Optional[Error]


class OnSupportRequest(BaseModel):
    context: dict
    message: dict
    error: Optional[Error]


class OnIssueRequest(BaseModel):
    context: dict
    message: dict
    error: Optional[Error]


class OnIssueStatusRequest(BaseModel):
    context: dict
    message: dict
    error: Optional[Error]


request_type_to_class_mapping = {
    "search": SearchRequest,
    "select": SelectRequest,
    "init": InitRequest,
    "confirm": ConfirmRequest,
    "status": StatusRequest,
    "track": TrackRequest,
    "cancel": CancelRequest,
    "update": UpdateRequest,
    "rating": RatingRequest,
    "support": SupportRequest,
    "issue": IssueRequest,
    "issue_status": IssueStatusRequest,
    "on_search": OnSearchRequest,
    "on_select": OnSelectRequest,
    "on_init": OnInitRequest,
    "on_confirm": OnConfirmRequest,
    "on_status": OnStatusRequest,
    "on_track": OnTrackRequest,
    "on_cancel": OnCancelRequest,
    "on_update": OnUpdateRequest,
    "on_rating": OnRatingRequest,
    "on_support": OnSupportRequest,
    "on_issue": OnIssueRequest,
    "on_issue_status": OnIssueStatusRequest,
}
