from pydantic import (BaseModel, model_validator, field_validator,
                      Field, ConfigDict)
from typing import List, Optional, Literal, Set

Status = Literal['active', 'non-active']


class UserSpec(BaseModel):
    user_id: int
    username: str
    surname: str
    second_name: Optional[str]
    email: str
    status: Status

    # @field_validator('email')
    # @classmethod
    # def check_email(cls, v: str) -> str:
    #     if '@' not in v or '.' not in v:
    #         raise ValueError('email должен содержать @ и .')
    #     return v


class ProfileSpec(UserSpec):
    bio: str
    url: str

    @field_validator('url')
    @classmethod
    def check_url(cls, v: str) -> str:
        if '://' not in v:
            raise ValueError("url должен содержать '://'")
        return v


class ItemSpec(BaseModel):
    item_id: int
    name: str
    desc: str
    price: float = Field(gt=0)
    model_config = ConfigDict(extra='forbid')

    @field_validator('name', mode='after')
    def validate_russian(cls, value):
        isRussian = all('а' <= char <= 'я' or 'А' <= char <= 'Я' or char.isspace()
                        for char in value)
        if not isRussian:
            raise ValueError("Field must contain only Russian alphabet characters")
        return value


class ServiceSpec(BaseModel):
    service_id: int
    name: str
    desc: str
    price: float = Field(gt=0)
    model_config = ConfigDict(extra='forbid')

    order_id: int
    order_line_id: int
    item_line: ItemSpec
    quantity: float = Field(gt=0)
    line_price: Optional[float] = Field(gt=0, default=None)
    model_config = ConfigDict(extra='forbid')

    @field_validator('name', mode='after')
    def validate_russian(cls, value):
        isRussian = all('а' <= char <= 'я' or 'А' <= char <= 'Я' or char.isspace()
                        for char in value)
        if not isRussian:
            raise ValueError("Field must contain only Russian alphabet characters")
        return value


class OrdersSpec(BaseModel):
    market_place_orders: List[ServiceSpec]
    model_config = ConfigDict(extra='forbid')

    @model_validator(mode='after')
    def check_lines(self):
        if not self.items_line:
            raise ValueError('items_line пустой')

        seen: Set[int] = set()
        for ln in self.items_line:
            if ln.order_id != self.order_id:
                raise ValueError(
                    'order_line.order_id должен '
                    'совпадать с order.order_id'
                )
            if ln.order_line_id in seen:
                raise ValueError(
                    f'повтор order_line_id '
                    f'внутри order {self.order_id}'
                )
            seen.add(ln.order_line_id)
        return self
