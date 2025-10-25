from pydantic import (
    BaseModel, model_validator, HttpUrl, computed_field, field_validator, ConfigDict, Field
)
from typing import List, Union, Optional, Literal, Annotated

RussianStr = Annotated[str, Field(pattern=r'^[А-Яа-яЁё\s\-0-9]+$')]

class UserSpec(BaseModel):
    """
    Модель профиля пользователя.

    Атрибуты:
    - user_id (int): Идентификатор пользователя.
    - username (str): Имя пользователя, состоящее из русских букв, пробелов, дефисов и цифр.
    - surname (str): Фамилия пользователя, состоящая из русских букв, пробелов, дефисов и цифр.
    - second_name (str, optional): Отчество пользователя, опционально.
    - email (str): Электронная почта пользователя, должна содержать '@' и '.'.
    - status (Literal['active', 'non-active']): Статус пользователя, может быть 'active' или 'non-active'.

    Конфигурация модели:
    - `extra='forbid'`: Запрещает наличие дополнительных полей, не указанных в модели.

    Валидаторы:
    - `validate_email`: Проверяет, что email содержит символы '@' и '.'.
    - username и surname должны состоять только из русских букв, пробелов, дефисов и цифр.
    - second_name может быть None, если не указано.
    - status должен быть либо 'active', либо 'non-active'.

    Пример использования:
        >>> user = UserSpec(
        ...     user_id=1,
        ...     username='Андрей',
        ...     surname='Савватеев',
        ...     second_name='Эдуардович',
        ...     email='deez@nu.ts',
        ...     status='active'
        ... )
        >>> print(user)
        user_id=1 username='Андрей' surname='Савватеев' second_name='Эдуардович' email='deez@nu.ts' status='active'
    """

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
    """Модель профиля пользователя с дополнительными полями.
    Наследуется от UserSpec(user_id, username, surname, second_name, email, status) и добавляет поля `bio` и `url`.

    Атрибуты:
    - bio (RussianStr): Краткая биография пользователя, состоящая из русских букв, пробелов, дефисов и цифр.
    - url (HttpUrl): URL пользователя, должен содержать '://'.

    Конфигурация модели:
    - `extra='forbid'`: Запрещает наличие дополнительных полей, не указанных в модели.

    Валидаторы:
    - `validate_url`: Проверяет, что URL содержит '://'.
    - `validate_bio`: Проверяет, что биография состоит только из русских букв, пробелов, дефисов и цифр.

    Пример использования:
        >>> profile = ProfileSpec(
        ...     user_id=1,
        ...     username='Андрей',
        ...     surname='Савватеев',
        ...     second_name='Эдуардович',
        ...     email='deez@nu.ts',
        ...     status='active',
        ...     bio='Программист и разработчик',
        ...     url='https://example.com/profile'
        ... )
        >>> print(profile)
        user_id=1 username='Андрей' surname='Савватеев' second_name='Эдуардович' email='deez@nu.ts' status='active' bio='Программист и разработчик' url='https://example.com/profile'
    """

    bio: RussianStr
    url: HttpUrl

    @field_validator('url', mode='after')
    @classmethod
    def validate_url(cls, value):
        if '://' not in str(value):
            raise ValueError("URL must contain '://'")
        return value


class ItemSpec(BaseModel):
    """
    Модель спецификации товара.

    Атрибуты:
    - item_id (int): Идентификатор товара.
    - name (str): Название товара, состоящее из русских букв, пробелов, дефисов и цифр.
    - desc (str): Описание товара, состоящее из русских букв, пробелов, дефисов и цифр.
    - price (float): Цена товара, должна быть больше 0.

    Конфигурация модели:
    - `extra='forbid'`: Запрещает наличие дополнительных полей, не указанных в модели.

    Валидаторы:
    - `validate_price`: Проверяет, что цена товара больше 0.
    - name и desc должны состоять только из русских букв, пробелов, дефисов и цифр.

    Пример использования:
        >>> item = ItemSpec(
        ...     item_id=1,
        ...     name='Товар 1',
        ...     desc='Описание товара 1',
        ...     price=100.0
        ... )
        >>> print(item)
        item_id=1 name='Товар 1' desc='Описание товара 1' price=100.0
    """

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
    """
    Модель услуги, которую предоставляет магазин.

    Атрибуты:
    - service_id (int): Идентификатор услуги.
    - name (str): Название услуги, состоящее из русских букв, пробелов, дефисов и цифр.
    - desc (str): Описание услуги, состоящее из русских букв, пробелов, дефисов и цифр.
    - price (float): Цена услуги, должна быть больше 0.

    Конфигурация модели:
    - `extra='forbid'`: Запрещает наличие дополнительных полей, не указанных в модели.

    Валидаторы:
    - `validate_price`: Проверяет, что цена услуги больше 0.
    - name и desc должны состоять только из русских букв, пробелов, дефисов и цифр.

    Пример использования:
        >>> service = ServiceSpec(
        ...     service_id=1,
        ...     name='Услуга 1',
        ...     desc='Описание услуги 1',
        ...     price=100.0
        ... )
        >>> print(service)
        service_id=1 name='Услуга 1' desc='Описание услуги 1' price=100.0
    """

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
    """
    Модель строки заказа, которая содержит информацию о товаре или услуге в заказе.

    Атрибуты:
    - order_id (int): Идентификатор заказа.
    - order_line_id (int): Идентификатор строки заказа, должен быть больше 0 и меньше или равен order_id.
    - item_line (Union[ServiceSpec, ItemSpec]): Товар или услуга, которая входит в строку заказа.
    - quantity (float): Количество товара или услуги в строке заказа, должно быть больше 0.

    Конфигурация модели:
    - `extra='forbid'`: Запрещает наличие дополнительных полей, не указанных в модели.

    Валидаторы:
    - `validate_quantity`: Проверяет, что количество больше 0.
    - `validate_order_line_id`: Проверяет, что order_line_id больше 0 и меньше или равен order_id.
    - `line_price`: Вычисляет цену строки заказа как произведение quantity и цены товара или услуги.

    Пример использования:
        >>> item = ItemSpec(item_id=1, name='Товар 1', desc='Описание товара 1', price=100.0)
        >>> order_line = OrderLineSpec(
        ...     order_id=1,
        ...     order_line_id=1,
        ...     item_line=item,
        ...     quantity=2.0
        ... )
        >>> print(order_line)
        order_id=1 order_line_id=1 item_line=ItemSpec(item_id=1, name='Товар 1', desc='Описание товара 1', price=100.0) quantity=2.0 line_price=200.0
    """

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
    """"
    Модель заказа, которая содержит информацию о заказе пользователя.

    Атрибуты:
    - order_id (int): Идентификатор заказа.
    - user_info (ProfileSpec): Профиль пользователя, который сделал заказ.
    - items_line (List[OrderLineSpec]): Список строк заказа, каждая из которых содержит информацию о товаре или услуге.

    Конфигурация модели:
    - `extra='forbid'`: Запрещает наличие дополнительных полей, не указанных в модели.
    
    Валидаторы:
    - `validate_order_id`: Проверяет, что order_id больше 0.
    - `validate_items_line`: Проверяет, что items_line не пустой и содержит только строки заказа с корректными order_id и order_line_id.

    Пример использования:
        >>> user_profile = ProfileSpec(
        ...     user_id=1,
        ...     username='Андрей',
        ...     surname='Савватеев',
        ...     second_name='Эдуардович',
        ...     email='andrey.savvateev@example.com',
        ...     status='active',
        ...     bio='Программист и разработчик',
        ...     url='https://example.com/profile'
        ... )
        >>> item = ItemSpec(item_id=1, name='Товар 1', desc='Описание товара 1', price=100.0)
        >>> order_line = OrderLineSpec(
        ...     order_id=1,
        ...     order_line_id=1,
        ...     item_line=item,
        ...     quantity=2.0
        ... )
        >>> order = OrderSpec(
        ...     order_id=1,
        ...     user_info=user_profile,
        ...     items_line=[order_line]
        ... )
        >>> print(order)
        order_id=1 user_info=ProfileSpec(user_id=1, username='Андрей', surname='Савватеев', second_name='Эдуардович', email='andrey.savvateev@example.com', status='active', bio='Программист и разработчик', url='https://example.com/profile') items_line=[OrderLineSpec(order_id=1, order_line_id=1, item_line=ItemSpec(item_id=1, name='Товар 1', desc='Описание товара 1', price=100.0), quantity=2.0)]
    """

    model_config = {
        "extra": "forbid"
    }
    order_id: int
    user_info: ProfileSpec
    items_line: List[OrderLineSpec]


class OrdersSpec(BaseModel):
    """
    Модель списка заказов, которая содержит информацию о заказах пользователей.

    Атрибуты:
    - market_place_orders (List[OrderSpec]): Список заказов на маркетплейсе.

    Конфигурация модели:
    - `extra='forbid'`: Запрещает наличие дополнительных полей, не указанных в модели.

    Пример использования:
        >>> user_profile = ProfileSpec(
        ...     user_id=1,
        ...     username='Андрей',
        ...     surname='Савватеев',
        ...     second_name='Эдуардович',
        ...     email='andrey.savvateev@example.com',
        ...     status='active',
        ...     bio='Программист и разработчик',
        ...     url='https://example.com/profile'
        ... )
        >>> item = ItemSpec(item_id=1, name='Товар 1', desc='Описание товара 1', price=100.0)
        >>> order_line = OrderLineSpec(
        ...     order_id=1,
        ...     order_line_id=1,
        ...     item_line=item,
        ...     quantity=2.0
        ... )
        >>> order = OrderSpec(
        ...     order_id=1,
        ...     user_info=user_profile,
        ...     items_line=[order_line]
        ... )
        >>> print(order)
        order_id=1 user_info=ProfileSpec(user_id=1, username='Андрей', surname='Савватеев', second_name='Эдуардович', email='andrey.savvateev@example.com', status='active', bio='Программист и разработчик', url='https://example.com/profile') items_line=[OrderLineSpec(order_id=1, order_line_id=1, item_line=ItemSpec(item_id=1, name='Товар 1', desc='Описание товара 1', price=100.0), quantity=2.0)]
    """

    model_config = {
        "extra": "forbid"
    }
    market_place_orders: List[OrderSpec]
