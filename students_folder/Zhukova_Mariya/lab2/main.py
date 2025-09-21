
from pydantic import BaseModel, field_validator, EmailStr, HttpUrl, model_validator, ConfigDict
from typing import Optional, Union, List
import re
import logging 
import yaml

# Логгер
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class UserSpec(BaseModel):
    user_id: int # НУЖНА УНИКАЛЬНОСТЬ!!!!!!!!!!!! - сделала в последнем классе
    username: str 
    surname: str 
    second_name: Optional[str]=None
    email: EmailStr
    status: str 

    model_config = ConfigDict(extra="forbid") # Запрещаем лишние поля

    # Проверка поля username на содержание только русского языка
    @field_validator("username", mode="after")
    @classmethod
    def check_russian_in_name(cls, value:str) -> str:
        if not re.match(r'^[А-Яа-яЁё\s\-]+$', value):
            raise ValueError("Поле username должно содержать только русский язык и быть не пустым")
        return value
    
    # Проверка поля surname на содержание только русского языка
    @field_validator("surname", mode="after") 
    @classmethod
    def check_russian_in_surname(cls, value:str) -> str:
        if not re.match(r'^[А-Яа-яЁё\s\-]+$', value):
            raise ValueError("Поле surname должно содержать только русский язык и быть не пустым")
        return value
    
    # Проверка поля статус на допустимые значения
    @field_validator("status", mode="after")
    @classmethod
    def check_status(cls, value:str) -> str:
        if value not in ["active", "non-active"]:
            raise ValueError("Поле status должно быть 'active' или 'non-active'")
        return value
    

class ProfileSpec(UserSpec):
    bio: str
    url: HttpUrl # url: Текстовое поле, не пустой, однозначно должны быть ://

    model_config = ConfigDict(extra="forbid") # Запрещаем лишние поля

    # Проверка поля bio на содержание только русского языка
    @field_validator("bio", mode="after")
    @classmethod
    def check_russian_in_bio(cls, value:str) -> str:
        if not re.match(r'^[А-Яа-яЁё\s\-]+$', value):
            raise ValueError("Поле username должно содержать только русский язык и быть не пустым")
        return value
    
class ItemSpec(BaseModel):
    item_id: int
    name: str # Русский алфавит
    desc: str # Русский алфавит
    price: float # >0

    model_config = ConfigDict(extra="forbid") # Запрещаем лишние поля

    # Проверка поля name на содержание только русского языка
    @field_validator("name", mode="after")
    @classmethod
    def check_russian_in_name(cls, value:str) -> str:
        if not re.match(r'^[А-Яа-яЁё\s\-]+$', value):
            raise ValueError("Поле name должно содержать только русский язык и быть не пустым")
        return value
    
    # Проверка поля desc на содержание только русского языка
    @field_validator("desc", mode="after") 
    @classmethod
    def check_russian_in_desc(cls, value:str) -> str:
        if not re.match(r'^[А-Яа-яЁё\s\-]+$', value):
            raise ValueError("Поле desc должно содержать только русский язык и быть не пустым")
        return value
    
    # Проверка поля price на допустимые значения
    @field_validator("price", mode="after")
    @classmethod
    def check_price(cls, value:float) -> float:
        if value <= 0:
            raise ValueError("Значение в поле price должно быть строго больше 0")
        return value
    

class ServiceSpec(BaseModel):
    service_id: int
    name: str # Русский алфавит
    desc: str # Русский алфавит
    price: float # >0

    model_config = ConfigDict(extra="forbid") # Запрещаем лишние поля

    # Проверка поля name на содержание только русского языка
    @field_validator("name", mode="after")
    @classmethod
    def check_russian_in_name(cls, value:str) -> str:
        if not re.match(r'^[А-Яа-яЁё\s\-]+$', value):
            raise ValueError("Поле name должно содержать только русский язык и быть не пустым")
        return value
    
    # Проверка поля desc на содержание только русского языка
    @field_validator("desc", mode="after") 
    @classmethod
    def check_russian_in_desc(cls, value:str) -> str:
        if not re.match(r'^[А-Яа-яЁё\s\-]+$', value):
            raise ValueError("Поле desc должно содержать только русский язык и быть не пустым")
        return value
    
    # Проверка поля price на допустимые значения
    @field_validator("price", mode="after")
    @classmethod
    def check_price(cls, value:float) -> float:
        if value <= 0:
            raise ValueError("Значение в поле price должно быть строго больше 0")
        return value
    

class OrderLineSpec(BaseModel):
    order_id: int
    order_line_id: int  # Уникальное значение в рамках одного order_id
    item_line: Union[ItemSpec, ServiceSpec]
    quantity: float
    line_price: float

    model_config = ConfigDict(extra="forbid")

    @field_validator("quantity", mode="after")
    @classmethod
    def check_quantity(cls, value: float) -> float:
        if value <= 0:
            raise ValueError("Значение в поле quantity должно быть строго больше 0")
        return value

    @model_validator(mode="after")
    def check_line_price(self):
        if self.line_price <= 0:
            raise ValueError("Значение в поле line_price должно быть строго больше 0")

        expected_price = self.item_line.price * self.quantity
        if abs(expected_price - self.line_price) > 1e-6:
            raise ValueError(f"line_price должно быть равно {expected_price}")
        return self
    

class OrderSpec(BaseModel):
    order_id: int
    user_info: ProfileSpec
    items_line: List[OrderLineSpec]
    
    model_config = ConfigDict(extra="forbid") # Запрещаем лишние поля


class OrdersSpec(BaseModel):
    market_place_orders: List[OrderSpec]

    model_config = ConfigDict(extra="forbid") # Запрещаем лишние поля

    @model_validator(mode="after")
    def check_global_uniques(self):
        user_ids = []
        item_ids = []
        service_ids = []
        order_ids = []

        for order in self.market_place_orders:
            order_ids.append(order.order_id)

            # user_id (из ProfileSpec)
            user_ids.append(order.user_info.user_id)

            # item_id / service_id
            for line in order.items_line:
                item_line = line.item_line
                if isinstance(item_line, ItemSpec):
                    item_ids.append(item_line.item_id)
                elif isinstance(item_line, ServiceSpec):
                    service_ids.append(item_line.service_id)

        # Проверки
        if len(user_ids) != len(set(user_ids)):
            raise ValueError("user_id должны быть уникальными")
        if len(order_ids) != len(set(order_ids)):
            raise ValueError("order_id должны быть уникальными")
        if len(item_ids) != len(set(item_ids)):
            raise ValueError("item_id должны быть уникальными")
        if len(service_ids) != len(set(service_ids)):
            raise ValueError("service_id должны быть уникальными")

        return self
    
if __name__ == "__main__":
    with open("./data.yaml", "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    orders = OrdersSpec(**data)

    logger.info(orders.model_dump_json(indent=2))

    

