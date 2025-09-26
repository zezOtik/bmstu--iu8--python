from pydantic import BaseModel, model_validator, HttpUrl, computed_field, field_validator
from typing import List, Union, Optional

class UserSpec(BaseModel):
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
    def validate_email(cls, value):
        if '@' not in value or '.' not in value:
            raise ValueError("Email must contain '@' and '.'")
        return value


class ProfileSpec(BaseModel):
    user_id: int
    username: str
    surname: str
    email: str
    status: str
    bio: str
    url: HttpUrl

    @field_validator('status', mode='after')
    def validate_status(cls, value):
        if value not in ['active', 'non-active']:
            raise ValueError("Status must be 'active' or 'non-active'")
        return value
    
    @field_validator('email', mode='after')
    def validate_email(cls, value):
        if '@' not in value or '.' not in value:
            raise ValueError("Email must contain '@' and '.'")
        return value

    @field_validator('bio', mode='after')
    def validate_bio(cls, value):
        isRussian = all('а' <= char <= 'я' or 'А' <= char <= 'Я' or char.isspace() for char in value)
        if not isRussian:
            raise ValueError("Bio must contain only Russian alphabet characters")
        return value

    @field_validator('url', mode='after')
    def validate_url(cls, value):
        if '://' not in value:
            raise ValueError("URL must contain '://'")
        return value

class ItemSpec(BaseModel):
    item_id: int
    name: str
    desc: str
    price: float

    @field_validator('name', mode='after')
    def validate_russian(cls, value):
        isRussian = all('а' <= char <= 'я' or 'А' <= char <= 'Я' or char.isspace() for char in value)
        if not isRussian:
            raise ValueError("Field must contain only Russian alphabet characters")
        return value
    
    @field_validator('desc', mode='after')
    def validate_russian_desc(cls, value):
        isRussian = all('а' <= char <= 'я' or 'А' <= char <= 'Я' or char.isspace() for char in value)
        if not isRussian:
            raise ValueError("Field must contain only Russian alphabet characters")
        return value

    @field_validator('price', mode='after')
    def validate_price(cls, value):
        if value <= 0:
            raise ValueError("Price must be greater than 0")
        return value
    
class ServiceSpec(BaseModel):
    service_id: int
    name: str
    desc: str
    price: float

    @field_validator('name', mode='after')
    def validate_russian(cls, value):
        isRussian = all('а' <= char <= 'я' or 'А' <= char <= 'Я' or char.isspace() for char in value)
        if not isRussian:
            raise ValueError("Field must contain only Russian alphabet characters")
        return value
    
    @field_validator('desc', mode='after')
    def validate_russian_desc(cls, value):
        isRussian = all('а' <= char <= 'я' or 'А' <= char <= 'Я' or char.isspace() for char in value)
        if not isRussian:
            raise ValueError("Field must contain only Russian alphabet characters")
        return value

    @field_validator('price', mode='after')
    def validate_price(cls, value):
        if value <= 0:
            raise ValueError("Price must be greater than 0")
        return value
    
class OrderLineSpec(BaseModel):
    order_id: int
    order_line_id: int
    item_line: Union[ServiceSpec, ItemSpec]
    quantity: float
    line_price: float

    @field_validator('quantity', mode='after')
    def validate_quantity(cls, value):
        if value <= 0:
            raise ValueError("Quantity must be greater than 0")
        return value
    
    @model_validator(mode='after')
    def validate_order_line_id(cls):
        if cls.order_line_id <= 0 or cls.order_line_id > cls.order_id:
            raise ValueError("Order line ID must be greater than 0 and less than or equal to order ID")
        return cls

    @computed_field
    def line_price(self) -> float:
        return self.quantity * self.item_line.price
    
class OrderSpec(BaseModel):
    order_id: int
    user_info: ProfileSpec
    items_line: List[OrderLineSpec]

class OrdersSpec(BaseModel):
    market_place_orders: List[OrderSpec]