import yaml
import logging

from pydantic import BaseModel, Field, model_validator, ConfigDict
from typing import Optional, Literal, List

from typing_extensions import Self

russian_regular = r'^[а-яА-ЯёЁ\s]+$'


class UserSpec(BaseModel):
    """Модель пользователя с валидацией email, username, surname, second_name, status.

    Атрибуты:
        user_id (int): Уникальный идентификатор пользователя.
        username (str): Имя пользователя. Только русские буквы
        surname (str): Фамилия пользователя. Только русские буквы
        second_name (str): Отчество пользователя. Опциональное поле. Только русские буквы
        email (str): Почта пользователя.
        status (str): Статус пользователя. Может быть только active или non-active

    Конфигурация:
        extra= "forbid": Запрещает передачу дополнительных полей,
        не объявленных в модели. При попытке передать неизвестное
        поле будет вызвано исключение ValidationError.

    Валидация:
        Поле `email` проходит валидацию через Field с паттерном `r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'`.
        Поля `username`, `surname`, `second_name` проходят валидацию через Field с паттерном `russian_regular` и
        минимальной длиной 1
        Поле `status` проходит валидацию через Literal.
        В случае не успешной валидации будет вызвано исключение ValidationError.

    Пример:
        >>> user = UserSpec(
        ... user_id=1,
        ... username='Алексей',
        ... surname="Земляков",
        ... second_name='Алексеевич',
        ... email='test@mail.com',
        ... status='active'
        ... )
        >>> print(user)
        user_id=1 username='Алексей' surname='Земляков' second_name='Алексеевич' email='test@mail.com' status='active'
    """

    user_id: int
    username: str = Field(min_length=1, pattern=russian_regular)
    surname: str = Field(min_length=1, pattern=russian_regular)
    second_name: Optional[str] = Field(pattern=russian_regular, default='')
    email: str = (
        Field(pattern=r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'))
    status: Literal['active', 'non-active']
    model_config = ConfigDict(extra='forbid')


class ProfileSpec(UserSpec):
    """Модель профиля пользователя, расширяющая базовую модель UserSpec.

         Наследует все поля и валидации от класса `UserSpec` (user_id, username, surname, second_name, email, status).
         и добавляет дополнительные поля `bio`, `url`.

         Атрибуты:
             bio (str): Биография пользователя. Только русские буквы
             url (str): Ссылка на аккаунт пользователя. Должно содержать ://

         Конфигурация:
             extra= "forbid": Запрещает передачу полей, не объявленных в модели
             (включая унаследованные от `UserSpec`). Любое неизвестное поле вызовет
             исключение `ValidationError`.

         Пример:
             >>> profile = ProfileSpec(
             ... user_id=2,
             ... username='Алексей',
             ... surname='Земляков',
             ... second_name='Алексеевич',
             ... email='test@mail.com',
             ... status='active',
             ... bio='Биография',
             ... url='http://example.com'
             ... )
             >>> print(profile)
             user_id=2 username='Алексей' surname='Земляков' second_name='Алексеевич' email='test@mail.com' status='active' bio='Биография' url='http://example.com'
         """

    bio: str = Field(min_length=1, pattern=russian_regular)
    url: str = Field(pattern=r'://')


class ItemSpec(BaseModel):
    """Модель элемента магазина с валидацией name, desc, price.

        Атрибуты:
            item_id (int): Уникальный идентификатор элемента.
            name (str): Наименование позиции. Только русские буквы
            desc (str): Описание. Только русские буквы
            price (float): Цена. Больше 0

        Конфигурация:
            extra= "forbid": Запрещает передачу дополнительных полей,
            не объявленных в модели. При попытке передать неизвестное
            поле будет вызвано исключение ValidationError.

        Валидация:
            Поля `name`, `desc` проходят валидацию через Field с паттерном `russian_regular` и минимальной длиной 1
            Поле `price` проходит валидацию через Field - требование - больше 0.
            В случае не успешной валидации будет вызвано исключение ValidationError.

        Пример:
            >>> item = ItemSpec(
            ... item_id=1,
            ... name='Доставка',
            ... desc="Клиентская доставка",
            ... price=10
            ... )
            >>> print(item)
            item_id=1 name='Доставка' desc='Клиентская доставка' price=10.0
        """
    item_id: int
    name: str = Field(min_length=1, pattern=russian_regular)
    desc: str = Field(min_length=1, pattern=russian_regular)
    price: float = Field(gt=0)
    model_config = ConfigDict(extra='forbid')


class ServiceSpec(BaseModel):
    """Модель сервисва, который предоставляет магазин с валидацией name, desc, price.

            Атрибуты:
                service_id (int): Уникальный идентификатор сервиса.
                name (str): Наименование сервиса. Только русские буквы
                desc (str): Описание. Только русские буквы
                price (float): Цена. Больше 0

            Конфигурация:
                extra= "forbid": Запрещает передачу дополнительных полей,
                не объявленных в модели. При попытке передать неизвестное
                поле будет вызвано исключение ValidationError.

            Валидация:
                Поля `name`, `desc` проходят валидацию через Field с паттерном `russian_regular` и минимальной длиной 1
                Поле `price` проходит валидацию через Field - требование - больше 0.
                В случае не успешной валидации будет вызвано исключение ValidationError.

            Пример:
                >>> service = ServiceSpec(
                ... service_id=1,
                ... name='Доставка',
                ... desc="Клиентская доставка",
                ... price=10
                ... )
                >>> print(service)
                service_id=1 name='Доставка' desc='Клиентская доставка' price=10.0
            """
    service_id: int
    name: str = Field(min_length=1, pattern=russian_regular)
    desc: str = Field(min_length=1, pattern=russian_regular)
    price: float = Field(gt=0)
    model_config = ConfigDict(extra='forbid')


class OrderLineSpec(BaseModel):
    """Модель строки заказа с валидацией quantity

        Атрибуты:
            order_id (int): Уникальный идентификатор заказа.
            order_line_id (int): Уникальный идентификатор строки заказа
            item_line (ItemSpec): Элемент заказа
            quantity (float): Количество. Больше 0
            line_price (float): Общая цена. Высчитывается после создания обьекта с помощью ```calculate_line_prices```

        Конфигурация:
            extra= "forbid": Запрещает передачу дополнительных полей,
            не объявленных в модели. При попытке передать неизвестное
            поле будет вызвано исключение ValidationError.

        Валидация:
            Поля `quantity`, `line_price` проходят валидацию через Field, должны быть больше 0.
            В случае не успешной валидации будет вызвано исключение ValidationError.

        Пример:
            >>> item = ItemSpec(
            ... item_id=1,
            ... name='Доставка',
            ... desc="Клиентская доставка",
            ... price=10
            ... )
            >>> order_line = OrderLineSpec(
            ... order_id=1,
            ... order_line_id=1,
            ... item_line=item,
            ... quantity=1
            ... )
            >>> print(order_line)
            order_id=1 order_line_id=1 item_line=ItemSpec(item_id=1, name='Доставка', desc='Клиентская доставка', price=10.0) quantity=1.0 line_price=10.0
        """

    order_id: int
    order_line_id: int
    item_line: ItemSpec
    quantity: float = Field(gt=0)
    line_price: Optional[float] = Field(gt=0, default=None)
    model_config = ConfigDict(extra='forbid')

    @model_validator(mode="after")
    def calculate_line_prices(self) -> Self:
        self.line_price = self.quantity * self.item_line.price
        return self


class OrderSpec(BaseModel):
    """Модель заказов пользователя

        Атрибуты:
            order_id (int): Уникальный идентификатор заказа.
            user_info (ProfileSpec): Профиль пользователя сделавшего заказ
            order_lines (List[OrderLineSpec]): Строки заказа

        Конфигурация:
            extra= "forbid": Запрещает передачу дополнительных полей,
            не объявленных в модели. При попытке передать неизвестное
            поле будет вызвано исключение ValidationError.

        Пример:
            >>> item = ItemSpec(
            ... item_id=1,
            ... name='Доставка',
            ... desc="Клиентская доставка",
            ... price=10
            ... )
            >>> order_line = OrderLineSpec(
            ... order_id=1,
            ... order_line_id=1,
            ... item_line=item,
            ... quantity=1
            ... )
            >>> profile = ProfileSpec(
            ... user_id=2,
            ... username='Алексей',
            ... surname='Земляков',
            ... second_name='Алексеевич',
            ... email='test@mail.com',
            ... status='active',
            ... bio='Биография',
            ... url='http://example.com'
            ... )
            >>> order_spec = OrderSpec(order_id=1, user_info=profile, order_lines=[order_line])

            >>> print(order_spec)
            order_id=1 user_info=ProfileSpec(user_id=2, username='Алексей', surname='Земляков', second_name='Алексеевич', email='test@mail.com', status='active', bio='Биография', url='http://example.com') order_lines=[OrderLineSpec(order_id=1, order_line_id=1, item_line=ItemSpec(item_id=1, name='Доставка', desc='Клиентская доставка', price=10.0), quantity=1.0, line_price=10.0)]
        """

    order_id: int
    user_info: ProfileSpec
    order_lines: List[OrderLineSpec]
    model_config = ConfigDict(extra='forbid')


class OrdersSpec(BaseModel):
    """Модель всех сделанных заказов

            Атрибуты:
                market_place_orders (List[OrderSpec]): Строки заказа

            Конфигурация:
                extra= "forbid": Запрещает передачу дополнительных полей,
                не объявленных в модели. При попытке передать неизвестное
                поле будет вызвано исключение ValidationError.

            Пример:
                >>> item = ItemSpec(
                ... item_id=1,
                ... name='Доставка',
                ... desc="Клиентская доставка",
                ... price=10
                ... )
                >>> order_line = OrderLineSpec(
                ... order_id=1,
                ... order_line_id=1,
                ... item_line=item,
                ... quantity=1
                ... )
                >>> profile = ProfileSpec(
                ... user_id=2,
                ... username='Алексей',
                ... surname='Земляков',
                ... second_name='Алексеевич',
                ... email='test@mail.com',
                ... status='active',
                ... bio='Биография',
                ... url='http://example.com'
                ... )
                >>> order_spec = OrderSpec(order_id=1, user_info=profile, order_lines=[order_line])
                >>> orders_spec = OrdersSpec(market_place_orders=[order_spec])

                >>> print(orders_spec)
                market_place_orders=[OrderSpec(order_id=1, user_info=ProfileSpec(user_id=2, username='Алексей', surname='Земляков', second_name='Алексеевич', email='test@mail.com', status='active', bio='Биография', url='http://example.com'), order_lines=[OrderLineSpec(order_id=1, order_line_id=1, item_line=ItemSpec(item_id=1, name='Доставка', desc='Клиентская доставка', price=10.0), quantity=1.0, line_price=10.0)])]
            """

    market_place_orders: List[OrderSpec]
    model_config = ConfigDict(extra='forbid')


def get_orders_from_yaml(yaml_data: dict) -> OrdersSpec | None:
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
        logging.info(f'Orders spec: {res}', exc_info=True)
        logging.info(f'Order spec first: {res.market_place_orders[0]}', exc_info=True)
        logging.info(f'Profile spec: {res.market_place_orders[0].user_info}',
                     exc_info=True)
        logging.info(f'Order line spec first: '
                     f'{res.market_place_orders[0].order_lines[0]}',
                     exc_info=True)
        logging.info(f'Item spec first:'
                     f' {res.market_place_orders[0].order_lines[0].item_line}',
                     exc_info=True)
except FileNotFoundError:
    logging.error('File not found')
except Exception as e:
    logging.error(f'Произошла ошибка при чтении файла: {e}')
