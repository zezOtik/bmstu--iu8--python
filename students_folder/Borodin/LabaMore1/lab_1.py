import logging
import yaml
from pydantic import BaseModel, Field, ConfigDict, model_validator
from pydantic import EmailStr, HttpUrl
from typing import Literal, Union, List

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')
RUS_RE = r'^[а-яА-ЯёЁ\s]+$'


class UserSpec(BaseModel):
    user_id:        int
    username:       str = Field(..., pattern=RUS_RE)
    surname:        str = Field(..., pattern=RUS_RE)
    second_name:    str = Field(None, pattern=RUS_RE)
    email:          EmailStr
    status:         Literal['active', 'non-active']
    model_config = ConfigDict(extra="forbid")

class ProfileSpec(UserSpec):
    bio:    str = Field(..., pattern=RUS_RE)
    url:    HttpUrl
    model_config = ConfigDict(extra="forbid")

class ItemSpec(BaseModel):
    item_id:    int
    name:       str = Field(..., pattern=RUS_RE)
    decs:       str = Field(..., pattern=RUS_RE)
    price:      float = Field(..., gt=0)
    model_config = ConfigDict(extra="forbid")

class ServiceSpec(BaseModel):
    service_id:     int
    name:           str = Field(..., pattern=RUS_RE)
    desc:           str = Field(..., pattern=RUS_RE)
    price:          float = Field(..., gt=0)
    model_config = ConfigDict(extra="forbid")

class OrderLineSpec(BaseModel):
    order_id:       int
    order_line_id:  int
    item_line:      Union[ServiceSpec, ItemSpec]
    quantity:       float = Field(..., gt=0)
    line_price:     float = Field(..., gt=0)

    @model_validator(mode='after')
    def check_line_prices(self):
        check = self.quantity * self.item_line.price
        if self.line_price != check:
            raise ValueError(f'line_price{self.line_price} != '
                            f'quantity * item_line.price{self.quantity * self.item_line.price}')
        return self
    
    model_config = ConfigDict(extra="forbid")
    
class OrderSpec(BaseModel):
    order_id:   int
    user_info:  ProfileSpec
    items_line: List[OrderLineSpec]

    model_config = ConfigDict(extra="forbid")

class OrdersSpec(BaseModel):
    market_place_orders:    List[OrderSpec]

    model_config = ConfigDict(extra="forbid")

def get_data_from_yaml(yaml_path: str) -> OrdersSpec:
    """
    Загружает и валидирует данные из YAML-файла с использованием Pydantic.
    """
    try:
        with open(yaml_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        orders = OrdersSpec.model_validate(data)
        logging.info("Данные успешно загружены и валидированы.")
        logging.info(orders.model_dump_json(indent=2, ensure_ascii=False))
        return orders
    except yaml.YAMLError as e:
        logging.error(f"Ошибка при чтении YAML: {e}")
        raise
    except Exception as e:
        logging.error(f"Ошибка валидации данных: {e}")
        raise

orders = get_data_from_yaml("students_folder/Borodin/LabaMore1/data.yaml")
