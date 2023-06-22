from enum import Enum
from typing import Optional

from pydantic import BaseModel, validator, ValidationError

from main.request_models.schema import Context, Catalog, Error


class Status(Enum):
    ACK = 'ACK'
    NACK = 'NACK'


class Message(BaseModel):
    catalog: Optional[Catalog]


class OnSearchRequest(BaseModel):
    context: Context
    message: Message
    error: Optional[Error]

    @validator("message")
    def validate_value(cls, v, values):
        """Validate each item"""
        if v.catalog is None:
            raise ValidationError("Catalog is missing!")
        return v


if __name__ == '__main__':
    some_dict = {
        "context": {
            "domain": "nic2004:52110",
            "country": "IND",
            "city": "std:080",
            "action": "on_search",
            "core_version": "1.0.0",
            "bap_id": "buyer-app.ondc.org",
            "bap_uri": "https://9c04-182-72-58-210.in.ngrok.io/protocol/v1",
            "transaction_id": "1fd6135c-6349-4b3b-b312-80ad4b780ff3",
            "message_id": "abd431a1-b266-48ed-9c4a-5e257a865624",
            "timestamp": "2022-09-19T08:22:15.322Z",
            "bpp_id": "ondcstage.hulsecure.in",
            "bpp_uri": "https://ondcstage.hulsecure.in/v1"
        },
        "message": {
            "catalog": {
                "bpp/descriptor": {
                    "name": "The UShop",
                    "symbol": "https://ushop.thesellerapp.com/img/ushop.png",
                    "short_desc": "The UShop",
                    "long_desc": "The UShop",
                    "images": [
                        "https://ushop.thesellerapp.com/img/ushop.png"
                    ]
                },
                "bpp/categories": [
                    {
                        "id": "Grocery",
                        "descriptor": {
                            "name": "Grocery",
                            "short_desc": "All kinds of Packaged Commodities"
                        }
                    }
                ],
                "bpp/fulfillments": [
                    {
                        "id": "cbd118f4-5d74-438b-a405-3a39055ca181",
                        "type": "Delivery",
                        "tracking": True,
                        "start": {
                            "location": {
                                "id": "65426587829",
                                "descriptor": {
                                    "name": "The UShop"
                                },
                                "gps": "12.9943, 77.7292"
                            },
                            "contact": {
                                "phone": "18008330506",
                                "email": "customercare@theushop.in"
                            }
                        }
                    }
                ],
                "bpp/providers": [
                ]
            }
        }
    }
    request = OnSearchRequest(**some_dict)
    print(request)