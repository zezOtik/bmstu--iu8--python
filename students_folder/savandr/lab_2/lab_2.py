from pydantic import (
    BaseModel, model_validator, HttpUrl, computed_field, field_validator
)
from typing import List, Union, Optional


class UserSpec(BaseModel):
    model_config = {
        "extra": "forbid"
    }
    user_id: int
    username: str
    surname: str
    second_name: Optional[str]
    email: str
    status: str

    @field_validator('status', mode='after')
    @classmethod
    def validate_status(cls, value):
        if value not in ['active', 'non-active']:
            raise ValueError("Status must be 'active' or 'non-active'")
        return value

    @field_validator('email', mode='after')
    def validate_email(self, value):
        if '@' not in value or '.' not in value:
            raise ValueError("Email must contain '@' and '.'")
        return value


class ProfileSpec(BaseModel):
    model_config = {
        "extra": "forbid"
    }
    user_id: int
    username: str
    surname: str
    email: str
    status: str
    bio: str
    url: HttpUrl

    @field_validator('status', mode='after')
    def validate_status(self, value):
        if value not in ['active', 'non-active']:
            raise ValueError("Status must be 'active' or 'non-active'")
        return value

    @field_validator('email', mode='after')
    def validate_email(self, value):
        if '@' not in value or '.' not in value:
            raise ValueError("Email must contain '@' and '.'")
        return value

    @field_validator('bio', mode='after')
    def validate_bio(self, value):
        is_russian = all(
            'а' <= char <= 'я' or 'А' <= char <= 'Я' or char.isspace()
            for char in value
        )
        if not is_russian:
            raise ValueError("Bio must contain only Russian alphabet characters")
        return value

    @field_validator('url', mode='after')
    def validate_url(self, value):
        if '://' not in value:
            raise ValueError("URL must contain '://'")
        return value


class ItemSpec(BaseModel):
    model_config = {
        "extra": "forbid"
    }
    item_id: int
    name: str
    desc: str
    price: float

    @field_validator('name', mode='after')
    def validate_name(self, value):
        is_russian = all(
            'а' <= char <= 'я' or 'А' <= char <= 'Я' or char.isspace()
            for char in value
        )
        if not is_russian:
            raise ValueError("Field must contain only Russian alphabet characters")
        return value

    @field_validator('desc', mode='after')
    def validate_desc(self, value):
        is_russian = all(
            'а' <= char <= 'я' or 'А' <= char <= 'Я' or char.isspace()
            for char in value
        )
        if not is_russian:
            raise ValueError("Field must contain only Russian alphabet characters")
        return value

    @field_validator('price', mode='after')
    def validate_price(self, value):
        if value <= 0:
            raise ValueError("Price must be greater than 0")
        return value


class ServiceSpec(BaseModel):
    model_config = {
        "extra": "forbid"
    }
    service_id: int
    name: str
    desc: str
    price: float

    @field_validator('name', mode='after')
    def validate_name(self, value):
        is_russian = all(
            'а' <= char <= 'я' or 'А' <= char <= 'Я' or char.isspace()
            for char in value
        )
        if not is_russian:
            raise ValueError("Field must contain only Russian alphabet characters")
        return value

    @field_validator('desc', mode='after')
    def validate_desc(self, value):
        is_russian = all(
            'а' <= char <= 'я' or 'А' <= char <= 'Я' or char.isspace()
            for char in value
        )
        if not is_russian:
            raise ValueError("Field must contain only Russian alphabet characters")
        return value

    @field_validator('price', mode='after')
    def validate_price(self, value):
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
    line_price: float

    @field_validator('quantity', mode='after')
    def validate_quantity(self, value):
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
