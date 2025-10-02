from pydantic import BaseModel, Field, EmailStr, HttpUrl, model_validator, ConfigDict
from typing import Optional, Union, List, Literal, Annotated
import logging
import yaml

# Логгер
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Аннотированный тип для русского алфавита в строках
RussianStr = Annotated[str, Field(pattern=r'^[А-Яа-яЁё\s\-]+$')]


class UserSpec(BaseModel):
    user_id: int
    username: RussianStr
    surname: RussianStr
    second_name: Optional[RussianStr] = None
    email: EmailStr
    status: Literal["active", "non-active"]

    model_config = ConfigDict(extra="forbid")  # Запрещаем лишние поля


class ProfileSpec(UserSpec):
    bio: RussianStr
    url: HttpUrl

    model_config = ConfigDict(extra="forbid")  # Запрещаем лишние поля


class ItemSpec(BaseModel):
    item_id: int
    name: RussianStr
    desc: RussianStr
    price: float = Field(gt=0)

    model_config = ConfigDict(extra="forbid")  # Запрещаем лишние поля


class ServiceSpec(BaseModel):
    service_id: int
    name: RussianStr
    desc: RussianStr
    price: float = Field(gt=0)

    model_config = ConfigDict(extra="forbid")  # Запрещаем лишние поля


class OrderLineSpec(BaseModel):
    order_id: int
    order_line_id: int
    item_line: Union[ItemSpec, ServiceSpec]
    quantity: float = Field(gt=0)
    line_price: float = Field(gt=0)

    model_config = ConfigDict(extra="forbid")

    @model_validator(mode="after")
    def check_line_price(self):
        expected_price = self.item_line.price * self.quantity
        if abs(expected_price - self.line_price) > 0:
            raise ValueError(f"line_price должно быть равно {expected_price}")
        return self


class OrderSpec(BaseModel):
    order_id: int
    user_info: ProfileSpec
    items_line: List[OrderLineSpec]

    model_config = ConfigDict(extra="forbid")

    @model_validator(mode="after")
    def check_unique_order_lines(self):
        order_line_ids = [line.order_line_id for line in self.items_line]
        if len(order_line_ids) != len(set(order_line_ids)):
            raise ValueError(f"order_line_id должны быть \
                             уникальными в рамках order_id={self.order_id}")
        return self


class OrdersSpec(BaseModel):
    market_place_orders: List[OrderSpec]

    model_config = ConfigDict(extra="forbid")

    @model_validator(mode="after")
    def check_global_uniques(self):
        user_ids = []
        item_ids = []
        service_ids = []
        order_ids = []

        for order in self.market_place_orders:
            order_ids.append(order.order_id)
            user_ids.append(order.user_info.user_id)

            for line in order.items_line:
                item_line = line.item_line
                if isinstance(item_line, ItemSpec):
                    item_ids.append(item_line.item_id)
                elif isinstance(item_line, ServiceSpec):
                    service_ids.append(item_line.service_id)

        if len(user_ids) != len(set(user_ids)):
            raise ValueError("user_id должны быть уникальными!")
        if len(order_ids) != len(set(order_ids)):
            raise ValueError("order_id должен быть уникальными!")
        if len(item_ids) != len(set(item_ids)):
            raise ValueError("item_id должны быть уникальными!")
        if len(service_ids) != len(set(service_ids)):
            raise ValueError("service_id должны быть уникальными!")

        return self


if __name__ == "__main__":
    try:
        with open("./data.yaml", "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        orders = OrdersSpec(**data)
        logger.info(orders.model_dump_json(indent=2))
    except FileNotFoundError:
        logger.error("Файл data.yaml не найден")
    except yaml.YAMLError as e:
        logger.error(f"Ошибка парсинга YAML: {e}")
    except Exception as e:
        logger.error(f"Произошла ошибка: {e}")
