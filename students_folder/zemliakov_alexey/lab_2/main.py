import yaml
import logging

from pydantic import BaseModel, Field, model_validator
from typing import Optional, Literal, List

from typing_extensions import Self


class UserSpec(BaseModel):
    user_id: int
    username: str = Field(min_length=1, pattern=r'^[а-яА-ЯёЁ\s]+$')
    surname: str = Field(min_length=1, pattern=r'^[а-яА-ЯёЁ\s]+$')
    second_name: Optional[str] = Field(pattern=r'^[а-яА-ЯёЁ\s]+$', default='')
    email: str = (
        Field(pattern=r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'))
    status: Literal['active', 'non-active']


class ProfileSpec(UserSpec):
    bio: str = Field(min_length=1, pattern=r'^[а-яА-ЯёЁ\s]+$')
    url: str = Field(pattern=r'://')


class ItemSpec(BaseModel):
    item_id: int
    name: str = Field(min_length=1, pattern=r'^[а-яА-ЯёЁ\s]+$')
    desc: str = Field(min_length=1, pattern=r'^[а-яА-ЯёЁ\s]+$')
    price: float = Field(gt=0)


class ServiceSpec(BaseModel):
    service_id: int
    name: str = Field(min_length=1, pattern=r'^[а-яА-ЯёЁ\s]+$')
    desc: str = Field(min_length=1, pattern=r'^[а-яА-ЯёЁ\s]+$')
    price: float = Field(gt=0)


class OrderLineSpec(BaseModel):
    order_id: int
    order_line_id: int
    item_line: ItemSpec
    quantity: float = Field(gt=0)
    line_price: Optional[float] = Field(gt=0, default=None)

    @model_validator(mode="after")
    def calculate_line_prices(self) -> Self:
        self.line_price = self.quantity * self.item_line.price
        return self


class OrderSpec(BaseModel):
    order_id: int
    user_info: ProfileSpec
    order_lines: List[OrderLineSpec]


class OrdersSpec(BaseModel):
    market_place_orders: List[OrderSpec]


def get_orders_from_yaml(yaml_data) -> OrdersSpec | None:
    if yaml_data and 'market_place_orders' in yaml_data:
        market_place_orders = yaml_data['market_place_orders']
        return OrdersSpec(market_place_orders=market_place_orders)
    return None


logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')
try:
    with open('data.yaml', 'r') as file:
        yaml_data = yaml.safe_load(file)
        res = get_orders_from_yaml(yaml_data)
except FileNotFoundError:
    print('File not found')
except Exception as e:
    print(f'Произошла ошибка при чтении файла {e}')

logging.info(f'Orders spec: {res}', exc_info=True)
logging.info(f'Order spec first: {res.market_place_orders[0]}', exc_info=True)
logging.info(f'Profile spec: {res.market_place_orders[0].user_info}',
             exc_info=True)
logging.info(f'Order line spec first: {res.market_place_orders[0].order_lines[0]}',
             exc_info=True)
logging.info(f'Item spec first: {res.market_place_orders[0].order_lines[0].item_line}',
             exc_info=True)
