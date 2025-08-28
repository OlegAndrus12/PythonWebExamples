from pydantic import BaseModel
from datetime import date
from pydantic import BaseModel, field_validator, ValidationError
from typing import List
from pprint import pprint

class OrderPydantic(BaseModel):
    order_id: int
    email_address: str
    checkout_date: date
    phone_number: str
    tags: List[str]

    @field_validator("email_address")
    def email_address_validator(cls, val):
        if not "@" in val:
            raise ValueError("Invalid email")
        return val

class OrdersList(BaseModel):
    list_name: str
    orders: List[OrderPydantic]


pprint(OrdersList.model_json_schema())