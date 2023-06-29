from enum import Enum
from typing import Optional

from pydantic import BaseModel, validator, ValidationError

from main.request_models.schema import Context, Catalog, Error, Intent


class Status(Enum):
    ACK = 'ACK'
    NACK = 'NACK'


class SearchMessage(BaseModel):
    intent: dict


class SearchRequest(BaseModel):
    context: Context
    message: SearchMessage
    error: Optional[Error]


class OnSearchMessage(BaseModel):
    catalog: Optional[Catalog]


class OnSearchRequest(BaseModel):
    context: Context
    message: OnSearchMessage
    error: Optional[Error]

    @validator("message")
    def validate_value(cls, v, values):
        """Validate each item"""
        if v.catalog is None:
            raise ValidationError("Catalog is missing!")
        return v


request_type_to_class_mapping = {
    "search": SearchRequest,
    "on_search": OnSearchRequest
}