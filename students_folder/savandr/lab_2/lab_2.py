from pydantic import (
    BaseModel, model_validator, HttpUrl, computed_field, field_validator, ConfigDict, Field
)
from typing import List, Union, Optional, Literal, Annotated

RussianStr = Annotated[str, Field(pattern=r'^[А-Яа-яЁё\s\-0-9]+$')]

class UserSpec(BaseModel):
    model_config = ConfigDict(extra='forbid')
    user_id: int
    username: RussianStr
    surname: RussianStr
    second_name: Optional[str] = None
    email: str
    status: Literal['active', 'non-active']

    @field_validator('email', mode='after')
    @classmethod
    def validate_email(cls, value):
        if '@' not in value or '.' not in value:
            raise ValueError("Email must contain '@' and '.'")
        return value


class ProfileSpec(UserSpec):
    bio: RussianStr
    url: HttpUrl

    @field_validator('url', mode='after')
    @classmethod
    def validate_url(cls, value):
        if '://' not in str(value):
            raise ValueError("URL must contain '://'")
        return value


class ItemSpec(BaseModel):
    model_config = {
        "extra": "forbid"
    }
    item_id: int
    name: RussianStr
    desc: RussianStr
    price: float

    @field_validator("price", mode="after")
    @classmethod
    def validate_price(cls, value: float) -> float:
        if value <= 0:
            raise ValueError("Price must be greater than 0")
        return value


class ServiceSpec(BaseModel):
    model_config = {
        "extra": "forbid",
        "populate_by_name": True
    }
    service_id: int
    name: RussianStr
    desc: RussianStr
    price: float

    @field_validator('price', mode='after')
    @classmethod
    def validate_price(cls, value):
        if value <= 0:
            raise ValueError("Price must be greater than 0")
        return value


class OrderLineSpec(BaseModel):
    model_config = {
        "extra": "forbid"
    }
    order_id: int
    order_line_id: int
    item_line: Union[ServiceSpec, ItemSpec]
    quantity: float

    @field_validator('quantity', mode='after')
    @classmethod
    def validate_quantity(cls, value):
        if value <= 0:
            raise ValueError("Quantity must be greater than 0")
        return value

    @model_validator(mode='after')
    def validate_order_line_id(self):
        if self.order_line_id <= 0 or self.order_line_id > self.order_id:
            raise ValueError("Wrong order line ID")
        return self

    @computed_field
    def line_price(self) -> float:
        return self.quantity * self.item_line.price


class OrderSpec(BaseModel):
    model_config = {
        "extra": "forbid"
    }
    order_id: int
    user_info: ProfileSpec
    items_line: List[OrderLineSpec]


class OrdersSpec(BaseModel):
    model_config = {
        "extra": "forbid"
    }
    market_place_orders: List[OrderSpec]
