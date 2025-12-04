import logging
import yaml
from pydantic import BaseModel, Field, ConfigDict, model_validator
from pydantic import EmailStr, HttpUrl
from typing import Literal, Union, List, Optional

# Настройка логирования
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Регулярное выражение для валидации кириллических строк (разрешены пробелы и дефисы)
RUS_RE = r'^[а-яА-ЯёЁ\s\-]+$'


class UserSpec(BaseModel):
    """Базовая модель пользователя маркетплейса.

    Атрибуты:
        user_id (int): Уникальный идентификатор пользователя. Должен быть > 0.
        username (str): Имя пользователя. Только кириллица, пробелы и дефисы.
        surname (str): Фамилия пользователя. Только кириллица, пробелы и дефисы.
        second_name (Optional[str]): Отчество пользователя. Может отсутствовать.
                                     Если задано — только кириллица, пробелы и дефисы.
        email (EmailStr): Корректный email-адрес.
        status (Literal['active', 'non-active']): Статус пользователя.

    Конфигурация:
        extra="forbid": Запрещает передачу дополнительных полей.

    Пример:
        >>> user = UserSpec(
        ...     user_id=101,
        ...     username="Иван",
        ...     surname="Иванов",
        ...     second_name="Иванович",
        ...     email="ivanov@example.com",
        ...     status="active"
        ... )
    """
    user_id: int = Field(..., gt=0)
    username: str = Field(..., pattern=RUS_RE)
    surname: str = Field(..., pattern=RUS_RE)
    second_name: Optional[str] = Field(None, pattern=RUS_RE)
    email: EmailStr
    status: Literal['active', 'non-active']
    model_config = ConfigDict(extra="forbid")


class ProfileSpec(UserSpec):
    """Расширенная модель профиля пользователя.

    Наследует все поля от `UserSpec` и добавляет:
    
    Атрибуты:
        bio (str): Биография пользователя. Только кириллица, пробелы, дефисы и базовая пунктуация (. , ! ?).
        url (HttpUrl): Ссылка на профиль. Только схемы `http` и `https`.

    Пример:
        >>> profile = ProfileSpec(
        ...     user_id=101,
        ...     username="Иван",
        ...     surname="Иванов",
        ...     second_name="Иванович",
        ...     email="ivanov@example.com",
        ...     status="active",
        ...     bio="Люблю покупать товары",
        ...     url="https://example.com/ivanov"
        ... )
    """
    bio: str = Field(..., pattern=RUS_RE)
    url: HttpUrl
    model_config = ConfigDict(extra="forbid")


class ItemSpec(BaseModel):
    """Спецификация товара (физического объекта) на маркетплейсе.

    Attributes:
        item_id (int): Уникальный идентификатор товара. Должен быть > 0.
        name (str): Название товара. Только кириллица, пробелы и дефисы.
        decs (str): Описание товара. Только кириллица, пробелы и дефисы.
        price (float): Цена товара в рублях. Должна быть > 0.
    """
    item_id: int = Field(..., gt=0)
    name: str = Field(..., pattern=RUS_RE)
    decs: str = Field(..., pattern=RUS_RE)
    price: float = Field(..., gt=0)
    model_config = ConfigDict(extra="forbid")


class ServiceSpec(BaseModel):
    """Модель услуги на маркетплейсе.

    Атрибуты:
        service_id (int): Уникальный идентификатор услуги (> 0).
        name (str): Название услуги. Только кириллица, пробелы и дефисы.
        desc (str): Описание услуги. Только кириллица, пробелы и дефисы.
        price (float): Стоимость услуги (> 0).

    Пример:
        >>> service = ServiceSpec(
        ...     service_id=2001,
        ...     name="Доставка",
        ...     desc="Быстрая доставка курьером",
        ...     price=500.0
        ... )
    """
    service_id: int = Field(..., gt=0)
    name: str = Field(..., pattern=RUS_RE)
    desc: str = Field(..., pattern=RUS_RE)
    price: float = Field(..., gt=0)
    model_config = ConfigDict(extra="forbid")


class OrderLineSpec(BaseModel):
    """Позиция в заказе: товар или услуга.

    Атрибуты:
        order_id (int): Идентификатор заказа (> 0).
        order_line_id (int): Идентификатор строки заказа (> 0).
        item_line (Union[ItemSpec, ServiceSpec]): Объект товара или услуги.
        quantity (float): Количество (> 0).
        line_price (float): Итоговая цена позиции (= quantity * item_line.price).

    Валидация:
        Автоматически проверяет, что `line_price == quantity * item_line.price`.

    Пример:
        >>> item = ItemSpec(item_id=1001, name="Ноутбук", desc="Геймерский", price=59999.99)
        >>> line = OrderLineSpec(
        ...     order_id=1,
        ...     order_line_id=10,
        ...     item_line=item,
        ...     quantity=1.0,
        ...     line_price=59999.99
        ... )
    """
    order_id: int = Field(..., gt=0)
    order_line_id: int = Field(..., gt=0)
    item_line: Union[ItemSpec, ServiceSpec]
    quantity: float = Field(..., gt=0)
    line_price: float = Field(..., gt=0)

    @model_validator(mode='after')
    def check_line_prices(self):
        """Проверяет корректность итоговой цены позиции."""
        calculated = self.quantity * self.item_line.price
        if self.line_price != calculated:
            raise ValueError(
                f'line_price {self.line_price} != '
                f'quantity * item_line.price {calculated}'
            )
        return self

    model_config = ConfigDict(extra="forbid")


class OrderSpec(BaseModel):
    """Полный заказ пользователя.

    Атрибуты:
        order_id (int): Уникальный идентификатор заказа (> 0).
        user_info (ProfileSpec): Профиль пользователя.
        items_line (List[OrderLineSpec]): Список позиций в заказе (может быть пустым).

    Пример:
        >>> profile = ProfileSpec(...)
        >>> line = OrderLineSpec(...)
        >>> order = OrderSpec(order_id=1, user_info=profile, items_line=[line])
    """
    order_id: int = Field(..., gt=0)
    user_info: ProfileSpec
    items_line: List[OrderLineSpec]
    model_config = ConfigDict(extra="forbid")


class OrdersSpec(BaseModel):
    """Контейнер для списка заказов.

    Атрибуты:
        market_place_orders (List[OrderSpec]): Список всех заказов.

    Пример:
        >>> order = OrderSpec(...)
        >>> orders = OrdersSpec(market_place_orders=[order])
    """
    market_place_orders: List[OrderSpec]
    model_config = ConfigDict(extra="forbid")


def get_data_from_yaml(yaml_path: str) -> OrdersSpec:
    """Загружает и валидирует данные из YAML-файла с использованием Pydantic.

    Эта функция:
    - читает YAML-файл по указанному пути,
    - парсит его в Python-объект,
    - выполняет валидацию через корневую модель `OrdersSpec`,
    - логирует результат при успехе,
    - выбрасывает исключение при ошибках.

    Args:
        yaml_path (str): Путь к YAML-файлу с данными о заказах.

    Returns:
        OrdersSpec: Валидированная структура данных.

    Raises:
        yaml.YAMLError: При ошибках разбора YAML.
        pydantic.ValidationError: При невалидных данных.
        Exception: При других ошибках валидации.
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


# Загрузка данных при импорте модуля (можно закомментировать в продакшене)
orders = get_data_from_yaml("students_folder/Borodin/LabaMore1/data.yaml")