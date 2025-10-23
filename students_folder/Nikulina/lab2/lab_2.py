from pydantic import BaseModel, Field, model_validator
from pydantic import EmailStr, HttpUrl
from pydantic import ConfigDict
from typing import Optional, List, Union, Set
from typing_extensions import Literal
import logging
import yaml


RUS_RE = r'^[А-Яа-яЁё][А-Яа-яЁё \-]*$'
Status = Literal['active', 'non-active']
logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)


class UserSpec(BaseModel):
    """Модель пользователя маркетплейса с валидацией имени пользователя,
    почты и статуса.

    Атрибуты:
        user_id (int): Уникальный идентификатор пользователя.
        username (str): Имя пользователя (кириллица).
        surname (str): Фамилия пользователя(кириллица).
        second_name (Optional[str]): Отчество пользователя (опционально, кириллица).
        email (EmailStr): Почта пользователя (Валидный e-mail).
        status (Literal['active','non-active']): Статус учётной записи.

    Конфигурация:
        extra="forbid": запрещает неописанные в модели поля.
        При попытке передать неизвестное поле будет вызвано 
        исключение ValidationError.

    Валидация:
        Поля `username`, `surname`, `second_name` проходит проверку по регулярному
        выражению `RUS_RE`. 
        Поле `email` автоматически валидируется типом `EmailStr` и должно содержать 
        корректный адрес в формате c @. 
        Поле `status` ограничено литералами `'active'` и `'non-active'`.
        При нарушении любого из условий валидации Pydantic выбрасывает
        исключение `ValidationError` с описанием поля и причины ошибки.

    Пример:
        >>> u = UserSpec(
        ... user_id=1,
        ... username="Екатерина",
        ... surname="Иванова",
        ... second_name="Николаевна",
        ... email="iv@example.com",
        ... status="active",
        ... )
        >>> print(u)
        user_id=1 username='Екатерина' surname='Иванова' second_name='Николаевна' email='iv@example.com' status='active'
    """
    user_id: int
    username: str = Field(..., pattern=RUS_RE)
    surname: str = Field(..., pattern=RUS_RE)
    second_name: Optional[str] = Field(None, pattern=RUS_RE)
    email: EmailStr
    status: Status

    model_config = ConfigDict(extra='forbid')

    # @field_validator('email')
    # @classmethod
    # def check_email(cls, v: str) -> str:
    #     if '@' not in v or '.' not in v:
    #         raise ValueError('email должен содержать @ и .')
    #     return v


class ProfileSpec(UserSpec):
    """Модель профиля пользователя, расширяющая базовую модель UserSpec.

    Наследует все поля и валидацию базового класса `UserSpec`
    (`user_id`, `username`, `surname`, `second_name`, `email`, `status`)
    и добавляет дополнительные атрибуты: `bio`, `url`.

    Атрибуты:
        bio (str): Короткая биография пользователя, только кириллица.
        url (HttpUrl): Валидный URL, начинающийся с протокола и с ://.

    Конфигурация:
        extra="forbid": Запрещает передачу дополнительных,
        неописанных в модели полей. 
        При попытке передать неизвестное поле будет вызвано 
        исключение `ValidationError`.

    Пример:
        >>> profile = ProfileSpec(
        ... user_id=2,
        ... username="Анна",
        ... surname="Смирнова",
        ... second_name="Евгеньевна",
        ... email="anna@example.com",
        ... status="active",
        ... bio="Покупатель",
        ... url="http://example.com"
        ... )
        >>> print(profile)
        user_id=2 username='Анна' surname='Смирнова' second_name='Евгеньевна' email='anna@example.com' 
        status='active' bio='Покупатель' url=HttpUrl('http://example.com/')
    """
    bio: str = Field(..., pattern=RUS_RE)
    url: HttpUrl

    # @field_validator('url')
    # @classmethod
    # def check_url(cls, v: str) -> str:
    #     if '://' not in v:
    #         raise ValueError("url должен содержать '://'")
    #     return v


class ItemSpec(BaseModel):
    """Модель товара в маркетплейсе с валидацией name, desc, price.

    Атрибуты:
        item_id (int): Уникальный идентификатор товара.
        name (str): Название товара. Должно соответствовать шаблону `RUS_RE`
            - допускаются кириллические символы.
        desc (str): Краткое описание товара. Также проверяется по шаблону `RUS_RE`.
        price (float): Стоимость единицы товара. Значение должно быть строго больше нуля.

    Конфигурация:
        extra='forbid': Запрещает передачу дополнительных полей, не описанных
        в модели. Любое лишнее поле приведёт к выбросу исключения `ValidationError`.

    Валидация:
        Поля `name`, `desc` проходят регулярную проверку соответствия шаблону `RUS_RE`  
          (только кириллица).  
        Поле `price` должно быть строго больше нуля (`gt=0`), иначе выбрасывается `ValidationError`.  
        Поле `item_id` проверяется на тип `int` и должно быть целым числом.  

        При несоответствии любому из условий автоматически выбрасывает
        исключение `ValidationError` с указанием проблемных полей и описанием ошибки.

    Пример:
        >>> item = ItemSpec(
        ... item_id=1,
        ... name="Кружка",
        ... desc="Керамическая кружка",
        ... price=20
        ... )
        >>> print(item)
        item_id=1 name='Кружка' desc='Керамическая кружка' price=20.0
    """
    item_id: int
    name: str = Field(..., pattern=RUS_RE)
    desc: str = Field(..., pattern=RUS_RE)
    price: float = Field(..., gt=0)

    model_config = ConfigDict(extra='forbid')


class ServiceSpec(BaseModel):
    """Модель услуги в маркетплейсе с валидацией name, desc, price.

    Атрибуты:
        service_id (int): Уникальный идентификатор услуги.
        name (str): Название услуги. Должно соответствовать регулярному выражению `RUS_RE`,
            допускается только кириллица.
        desc (str): Краткое описание услуги. Также проверяется по шаблону `RUS_RE`.
        price (float): Стоимость услуги, выраженная числом с плавающей точкой.
            Должна быть строго больше нуля.

    Конфигурация:
        extra="forbid": Запрещает передачу дополнительных,
        неописанных в модели полей. При попытке передать неизвестное
        поле будет вызвано исключение `ValidationError`.

    Валидация:
        Поля `name` и `desc` проходят проверку по регулярному выражению `RUS_RE`.
        Поле `price` должно быть строго положительным (`gt=0`).
          Если значение не удовлетворяет этому условию, будет выброшено исключение `ValidationError`.
        Поле `service_id` должно быть целым числом.

    Пример:
        >>> service = ServiceSpec(
        ... service_id=5,
        ... name="Доставка",
        ... desc="Курьерьеская доставка",
        ... price=250
        ... )
        >>> print(service)
        service_id=5 name='Доставка' desc='Курьерьеская доставка' price=250.0
    """
    service_id: int
    name: str = Field(..., pattern=RUS_RE)
    desc: str = Field(..., pattern=RUS_RE)
    price: float = Field(..., gt=0)

    model_config = ConfigDict(extra='forbid')


class OrderLineSpec(BaseModel):
    """Модель строки заказа с валидацией quantity.

    Атрибуты:
        order_id (int): Идентификатор заказа.
        order_line_id (int): Уникальный идентификатор строки внутри конкретного заказа.
        item_line (Union[ServiceSpec, ItemSpec]): Позиция заказа.
        quantity (float): Количество товара или услуг. Значение должно быть строго больше нуля.
        line_price (float): Итоговая сумма. Должна равняться `quantity * item_line.price`.

    Конфигурация:
        extra="forbid": Запрещает передачу дополнительных,
        неописанных в модели полей. При попытке передать неизвестное
        поле будет вызвано исключение `ValidationError`.

    Валидация:
        Проверяется, что `quantity > 0` и `line_price > 0`.  
        При помощи валидатора `check_line_price` выполняется логическая проверка:
          `line_price` должно совпадать с произведением `quantity * item_line.price`.  
        Если значения не совпадают, Pydantic автоматически выбрасывает исключение `ValidationError`
          с описанием несоответствия.

    Пример:
        >>> item = ItemSpec(
        ... item_id=1,
        ... name="Кружка",
        ... desc="Керамическая кружка",
        ... price=20
        ... )
        >>> line = OrderLineSpec(
        ... order_id=1,
        ... order_line_id=1,
        ... item_line=item,
        ... quantity=1,
        ... line_price=20
        ... )
        >>> print(line)
        order_id=1 order_line_id=1 item_line=ItemSpec(item_id=1, name='Кружка', desc='Керамическая кружка', price=20.0) 
        quantity=1.0 line_price=20.0
    """
    order_id: int
    order_line_id: int
    item_line: Union[ServiceSpec, ItemSpec]
    quantity: float = Field(..., gt=0)
    line_price: float = Field(..., gt=0)

    model_config = ConfigDict(extra='forbid')

    @model_validator(mode='after')
    def check_line_price(self):
        """Проверяет согласованность суммы строки заказа.

        Returns:
            Object: Валидированный экземпляр модели OrderLineSpec.

        Raises:
            ValueError: Если `line_price` не совпадает с рассчитанным значением.
        """
        expected = self.quantity * self.item_line.price
        if self.line_price != expected:
            raise ValueError(
                f'line_price не равно quantity * item_line.price '
                f'({self.line_price} != {self.quantity} * '
                f'{self.item_line.price} = {expected})'
            )
        return self


class OrderSpec(BaseModel):
    """Модель заказа в маркетплейсе.

    Атрибуты:
        order_id (int): Уникальный идентификатор заказа.
        user_info (ProfileSpec): Профиль пользователя, оформившего заказ.
        items_line (List[OrderLineSpec]): Список строк заказа.

    Конфигурация:
        extra="forbid": Запрещает передачу дополнительных,
        неописанных в модели полей. При попытке передать неизвестное
        поле будет вызвано исключение `ValidationError`.

    Валидация:
        Проверяется, что список `items_line` не пуст.  
        У каждой строки `OrderLineSpec` значение `order_id` совпадает с `order.order_id`.  
        Поля `order_line_id` внутри одного заказа должны быть уникальными.  
        При обнаружении нарушений создаётся исключение `ValidationError` 
        с подробным описанием ошибки.

    Пример:
        >>> profile = ProfileSpec(
        ... user_id=10,
        ... username="Андрей",
        ... surname="Кузнецов",
        ... second_name="Николаевич",
        ... email="andrey@example.com",
        ... status="active",
        ... bio="Клиент",
        ... url="http://example.com"
        ... )
        >>> item = ItemSpec(
        ... item_id=1,
        ... name="Кружка",
        ... desc="Керамическая кружка",
        ... price=20
        ... )
        >>> line = OrderLineSpec(
        ... order_id=1,
        ... order_line_id=1,
        ... item_line=item,
        ... quantity=1,
        ... line_price=20
        ... )
        >>> order = OrderSpec(
        ... order_id=1,
        ... user_info=profile,
        ...  items_line=[line]
        ... )
        >>> print(order)
        order_id=1 user_info=ProfileSpec(user_id=10, username='Андрей', surname='Кузнецов', second_name='Николаевич',
        email='andrey@example.com', status='active', bio='Клиент', url=HttpUrl('http://example.com', ))
        items_line=[OrderLineSpec(order_id=1, order_line_id=1, item_line=ItemSpec(item_id=1, name='Кружка',
        desc='Керамическая кружка', price=20.0), quantity=1.0, line_price=20.0)]
    """
    order_id: int
    user_info: ProfileSpec
    items_line: List[OrderLineSpec]

    model_config = ConfigDict(extra='forbid')

    @model_validator(mode='after')
    def check_lines(self):
        """Проверяет корректность строк заказа.

        Returns:
            Object: Валидированный экземпляр модели OrderSpec.

        Raises:
            ValueError: Если список строк пуст, встречаются дублирующиеся индентификаторы.
        """
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


class OrdersSpec(BaseModel):
    """Модель набора заказов маркетплейса.

    Атрибуты:
        market_place_orders (List[OrderSpec]): Список всех заказов маркетплейса.

    Конфигурация:
        extra="forbid": Запрещает передачу дополнительных,
        неописанных в модели полей. При попытке передать неизвестное
        поле будет вызвано исключение `ValidationError`.

    Валидация:
        Проверяется, что каждый `order_id` встречается только один раз
          среди всех заказов.
        Проверяется уникальность `user_id` - один пользователь не может
          встречаться в нескольких заказах в пределах одной структуры.
        Проверяется, что `item_id` для товаров и `service_id` для услуг
          не дублируются среди всех заказов. 
        При нарушении любого из условий будет выброшено исключение `ValidationError`.

    Пример:
        >>> profile = ProfileSpec(
        ... user_id=21,
        ... username="Сергей",
        ... surname="Павлов",
        ... second_name=None,
        ... email="sergey@example.com",
        ... status="active",
        ... bio="Клиент",
        ... url="http://example.com"
        ... )
        >>> service = ServiceSpec(
        ... service_id=8,
        ... name="Доставка",
        ... desc="Курьерская доставка",
        ... price=300
        ... )
        >>> line = OrderLineSpec(
        ... order_id=1,
        ... order_line_id=1,
        ... item_line=service,
        ... quantity=1,
        ... line_price=300
        ... )
        >>> order = OrderSpec(
        ... order_id=1,
        ... user_info=profile,
        ... items_line=[line]
        ... )
        >>> orders = OrdersSpec(market_place_orders=[order])
        >>> print(orders)
        market_place_orders=[OrderSpec(order_id=1, user_info=ProfileSpec(user_id=21, username='Сергей', surname='Павлов',
        second_name=None, email='sergey@example.com', status='active', bio='Клиент', url=HttpUrl('http://example.com', )),
        items_line=[OrderLineSpec(order_id=1, order_line_id=1, item_line=ServiceSpec(service_id=8, name='Доставка', desc='Курьерская доставка',
        price=300.0), quantity=1.0, line_price=300.0)])]
    """
    market_place_orders: List[OrderSpec]

    model_config = ConfigDict(extra='forbid')

    @model_validator(mode='after')
    def check_global_uniques(self):
        """Проверяет глобальные уникальности идентификаторов во всех заказах.

        Returns:
            Object: Валидированный экземпляр модели OrdersSpec.

        Raises:
            ValueError: Если встречаются повторяющиеся идентификаторы.
        """
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
                        raise ValueError(
                            f'повторяющийся '
                            f'item_id: {il.item_id}'
                        )
                    item_ids.add(il.item_id)
                else:
                    if il.service_id in service_ids:
                        raise ValueError(
                            f'повторяющийся '
                            f'service_id: {il.service_id}'
                        )
                    service_ids.add(il.service_id)
        return self


def load(yaml_text: str) -> OrdersSpec:
    data = yaml.safe_load(yaml_text)
    return OrdersSpec(**data)


def main():
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
                f'order_id={ln.order_id}, '
                f'количество={ln.quantity}, '
                f'цена={ln.line_price}'
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


if __name__ == '__main__':
    main()
