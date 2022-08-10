from enum import Enum


class SubscriberType(Enum):
    BAP = "BAP",
    BPP = "BPP",
    BG = "BG",
    LREG = "LREG",
    CREG = "CREG",
    RREG = "RREG"


subscriber_type_mapping = {
    "BG": "gateway",
    "BAP": "buyerApp",
    "BPP": "sellerApp",
}
