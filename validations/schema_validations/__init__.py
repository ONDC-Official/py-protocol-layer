import pydantic

from models.error import BaseError
from utils.ack_utils import get_ack_response
from validations.schema_validations.models.request import *


def validate_request_type(payload, request_type):
    if request_type == payload["context"]["action"]:
        return None
    else:
        return get_ack_response(context=payload["context"], ack=False,
                                error={"type": BaseError.JSON_SCHEMA_ERROR.value, "code": "20000",
                                       "message": f"Context.action doesn't match the route {request_type}!"})


def validate_schema(payload, request_type):
    try:
        request_type_to_class_mapping[request_type](**payload)
        return None
    except pydantic.ValidationError as e:
        error_message = str(e)
        return get_ack_response(context=payload["context"], ack=False,
                                error={"type": BaseError.JSON_SCHEMA_ERROR.value, "code": "20000",
                                       "message": error_message})


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
    "full_on_search": FullOnSearchRequest,
    "inc_on_search": IncrOnSearchRequest,
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
