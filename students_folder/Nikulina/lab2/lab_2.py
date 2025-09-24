from pydantic import BaseModel, Field, field_validator, model_validator
from typing import Optional, List, Union, Set
from typing_extensions import Literal
import logging
import yaml

RUS_RE = r'^[А-Яа-яЁё][А-Яа-яЁё \-]*$' 
Status = Literal['active', 'non-active'] 
logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s') 
logger = logging.getLogger(__name__)

class UserSpec(BaseModel):
    user_id: int
    username: str = Field(..., pattern=RUS_RE)
    surname: str = Field(..., pattern=RUS_RE)
    second_name: Optional[str] = Field(None, pattern=RUS_RE)
    email: str
    status: Status

    class Config:
        extra = 'forbid'

    @field_validator('email')
    @classmethod
    def check_email(cls, v: str) -> str:
        if '@' not in v or '.' not in v:
            raise ValueError('email должен содержать @ и .')
        return v

class ProfileSpec(UserSpec):
    bio: str = Field(..., pattern=RUS_RE)
    url: str

    @field_validator('url')
    @classmethod
    def check_url(cls, v: str) -> str:
        if '://' not in v:
            raise ValueError("url должен содержать '://'")
        return v
    
class ItemSpec(BaseModel):
    item_id: int
    name: str = Field(..., pattern=RUS_RE)
    desc: str = Field(..., pattern=RUS_RE)
    price: float = Field(..., gt=0)

    class Config:
        extra = 'forbid'

class ServiceSpec(BaseModel):
    service_id: int
    name: str = Field(..., pattern=RUS_RE)
    desc: str = Field(..., pattern=RUS_RE)
    price: float = Field(..., gt=0)

    class Config:
        extra = 'forbid'

class OrderLineSpec(BaseModel):
    order_id: int
    order_line_id: int
    item_line: Union[ServiceSpec, ItemSpec]
    quantity: float = Field(..., gt=0)
    line_price: float = Field(..., gt=0)

    class Config:
        extra = 'forbid'

    @model_validator(mode='after')
    def check_line_price(self):
        expected = self.quantity * self.item_line.price
        if self.line_price != expected:
            raise ValueError(
                f'line_price не равно quantity * item_line.price '
                f'({self.line_price} != {self.quantity} * {self.item_line.price} = {expected})'
            )
        return self

class OrderSpec(BaseModel):
    order_id: int
    user_info: ProfileSpec
    items_line: List[OrderLineSpec]

    class Config:
        extra = 'forbid'

    @model_validator(mode='after')
    def check_lines(self):
        if not self.items_line:
            raise ValueError('items_line пустой')

        seen: Set[int] = set()
        for ln in self.items_line:
            if ln.order_id != self.order_id:
                raise ValueError('order_line.order_id должен совпадать с order.order_id')
            if ln.order_line_id in seen:
                raise ValueError(f'повтор order_line_id внутри order {self.order_id}')
            seen.add(ln.order_line_id)
        return self

class OrdersSpec(BaseModel):
    market_place_orders: List[OrderSpec]

    class Config:
        extra = 'forbid'

    @model_validator(mode='after')
    def check_global_uniques(self):
        order_ids: Set[int] = set()
        user_ids: Set[int] = set()
        item_ids: Set[int] = set()
        service_ids: Set[int] = set()

        for o in self.market_place_orders:
            if o.order_id in order_ids:
                raise ValueError(f'повторяющийся order_id: {o.order_id}')
            order_ids.add(o.order_id)

            uid = o.user_info.user_id
            if uid in user_ids:
                raise ValueError(f'повторяющийся user_id: {uid}')
            user_ids.add(uid)

            for ln in o.items_line:
                il = ln.item_line
                if isinstance(il, ItemSpec):
                    if il.item_id in item_ids:
                        raise ValueError(f'повторяющийся item_id: {il.item_id}')
                    item_ids.add(il.item_id)
                else:
                    if il.service_id in service_ids:
                        raise ValueError(f'повторяющийся service_id: {il.service_id}')
                    service_ids.add(il.service_id)
        return self

def load(yaml_text: str) -> OrdersSpec:
    data = yaml.safe_load(yaml_text)
    return OrdersSpec(**data)


if __name__ == '__main__':
    with open("data.yaml", "r", encoding="utf-8") as f:
        yaml_text = f.read()
    orders = load(yaml_text)

for o in orders.market_place_orders:
    logger.info(f'order_id={o.order_id}')

    u = o.user_info
    logger.info(
        f'id={u.user_id}, '
        f'ФИО: {u.surname} {u.username} {u.second_name}, '
        f'email={u.email}, статус={u.status}, био={u.bio}, url={u.url}'
    )

    for ln in o.items_line:
        logger.info(
            f'строка заказа={ln.order_line_id}, '
            f'order_id={ln.order_id}, количество={ln.quantity}, цена={ln.line_price}'
        )

        if isinstance(ln.item_line, ServiceSpec):
            s = ln.item_line
            logger.info(
                f'service_id={s.service_id}, '
                f'наименование={s.name}, описание={s.desc}, цена={s.price}'
            )
        else:
            it = ln.item_line
            logger.info(
                f'item_id={it.item_id}, '
                f'наименование={it.name}, описание={it.desc}, цена={it.price}'
            )

logger.info(f'всего заказов = {len(orders.market_place_orders)}')
