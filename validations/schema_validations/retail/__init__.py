
from validations.schema_validations.retail.models.request import *


def validate_retail_schema(payload, request_type):
    retail_request_type_to_class_mapping[request_type](**payload)


retail_request_type_to_class_mapping = {
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