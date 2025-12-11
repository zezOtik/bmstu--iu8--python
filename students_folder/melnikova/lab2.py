from pydantic import (BaseModel, model_validator, field_validator,
                      Field, ConfigDict, HttpUrl)
from typing import List, Optional, Literal, Set

Status = Literal['active', 'non-active']
RUS_RE = r'^[А-Яа-яЁё][А-Яа-яЁё \-]*$'


class UserSpec(BaseModel):
    """
       Базовая модель пользователя.

       Attributes:
           user_id: Уникальный идентификатор пользователя
           username: Имя пользователя
           surname: Фамилия
           second_name: Отчество (опционально)
           email: Email адрес
           status: Статус пользователя ('active' или 'non-active')
       """
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
    model_config = ConfigDict(extra='forbid')


class ProfileSpec(UserSpec):
    """
       Расширенный профиль пользователя.

       Наследует все поля UserSpec и добавляет:
           bio: Краткая биография пользователя
           url: Валидный URL адрес профиля
       """
    bio: str
    url: HttpUrl

    # @field_validator('url')
    # @classmethod
    # def check_url(cls, v: str) -> str:
    #   if '://' not in v:
    #       raise ValueError("url должен содержать '://'")
    #   return v

    model_config = ConfigDict(extra='forbid')

class ItemSpec(BaseModel):
    """
       Модель товара/продукта.

       Attributes:
           item_id: Уникальный идентификатор товара
           name: Название товара (только русские буквы)
           desc: Описание товара (только русские буквы)
           price: Цена товара (должна быть больше 0)
       """
    item_id: int
    name: str = Field(..., pattern=RUS_RE)
    desc: str = Field(..., pattern=RUS_RE)
    price: float = Field(gt=0)
    model_config = ConfigDict(extra='forbid')

    #@field_validator('name', mode='after')
    #def validate_russian(self, value):
    #    is_russian = all('а' <= char <= 'я' or 'А' <= char <= 'Я' or char.isspace()
    #                     for char in value)
    #    if not is_russian:
    #        raise ValueError("Field must contain only Russian alphabet characters")
    #    return value


class ServiceSpec(BaseModel):
    """
       Модель услуги/сервиса.

       Attributes:
           service_id: Уникальный идентификатор услуги
           name: Название услуги
           desc: Описание услуги
           price: Стоимость услуги
           order_id: ID заказа
           order_line_id: ID строки заказа
           item_line: Связанный товар
           quantity: Количество
           line_price: Итоговая цена строки (автоматически рассчитывается)
       """
    service_id: int
    name: str = Field(..., pattern=RUS_RE)
    desc: str = Field(..., pattern=RUS_RE)
    price: float = Field(gt=0)
    model_config = ConfigDict(extra='forbid')

    order_id: int
    order_line_id: int
    item_line: ItemSpec
    quantity: float = Field(gt=0)
    line_price: Optional[float] = Field(gt=0, default=None)
    model_config = ConfigDict(extra='forbid')

    #@field_validator('name', mode='after')
    #def validate_russian(self, value):
    #    is_russian = all('а' <= char <= 'я' or 'А' <= char <= 'Я' or char.isspace()
    #                     for char in value)
    #    if not is_russian:
    #        raise ValueError("Field must contain only Russian alphabet characters")
    #    return value

    model_config = ConfigDict(extra='forbid')


class OrdersSpec(BaseModel):
    """
        Модель заказов.

        Attributes:
            market_place_orders: Список услуг/сервисов в заказе

        Validators:
            Проверяет, что список не пустой
            Проверяет уникальность order_line_id
            Проверяет соответствие order_id
        """
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

    model_config = ConfigDict(extra='forbid')
