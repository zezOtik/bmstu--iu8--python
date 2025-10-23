"""
Модуль для работы с заказами маркетплейса.

Содержит Pydantic модели для валидации данных пользователей,
товаров, услуг и заказов с комплексной проверкой бизнес-правил.
"""

from pydantic import BaseModel, Field, EmailStr, HttpUrl, model_validator, ConfigDict
from typing import Optional, Union, List, Literal, Annotated
import logging
import yaml

# Логгер
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Аннотированный тип для русских строк
RussianStr = Annotated[str, Field(pattern=r'^[А-Яа-яЁё\s\-]+$')]


class UserSpec(BaseModel):
    """Модель пользователя маркетплейса.

    Attributes:
        user_id: Уникальный идентификатор пользователя.
        username: Имя пользователя на русском языке.
        surname: Фамилия пользователя на русском языке.
        second_name: Отчество пользователя (опционально).
        email: Email пользователя в валидном формате.
        status: Статус пользователя (active/non-active).
    """

    user_id: int
    username: RussianStr
    surname: RussianStr
    second_name: Optional[RussianStr] = None
    email: EmailStr
    status: Literal["active", "non-active"]

    model_config = ConfigDict(extra="forbid")  # Запрещаем лишние поля


class ProfileSpec(UserSpec):
    """Расширенная модель профиля пользователя.

    Attributes:
        bio: Биография пользователя на русском языке.
        url: URL страницы профиля в валидном формате.
    """

    bio: RussianStr
    url: HttpUrl

    model_config = ConfigDict(extra="forbid")  # Запрещаем лишние поля


class ItemSpec(BaseModel):
    """Модель товара в маркетплейсе.

    Attributes:
        item_id: Уникальный идентификатор товара.
        name: Название товара на русском языке.
        desc: Описание товара на русском языке.
        price: Цена товара (должна быть больше 0).
    """

    item_id: int
    name: RussianStr
    desc: RussianStr
    price: float = Field(gt=0)

    model_config = ConfigDict(extra="forbid")  # Запрещаем лишние поля


class ServiceSpec(BaseModel):
    """Модель услуги в маркетплейсе.

    Attributes:
        service_id: Уникальный идентификатор услуги.
        name: Название услуги на русском языке.
        desc: Описание услуги на русском языке.
        price: Цена услуги (должна быть больше 0).
    """

    service_id: int
    name: RussianStr
    desc: RussianStr
    price: float = Field(gt=0)

    model_config = ConfigDict(extra="forbid")  # Запрещаем лишние поля


class OrderLineSpec(BaseModel):
    """Модель строки заказа.

    Attributes:
        order_id: Идентификатор заказа.
        order_line_id: Идентификатор строки заказа.
        item_line: Товар или услуга в заказе.
        quantity: Количество (должно быть больше 0).
        line_price: Стоимость строки (должна быть больше 0).

    Raises:
        ValueError: Если line_price не соответствует произведению цены на количество.
    """

    order_id: int
    order_line_id: int
    item_line: Union[ItemSpec, ServiceSpec]
    quantity: float = Field(gt=0)
    line_price: float = Field(gt=0)

    model_config = ConfigDict(extra="forbid")

    @model_validator(mode="after")
    def check_line_price(self):
        """Проверяет соответствие line_price произведению цены на количество.

        Returns:
            self: Валидированный объект.

        Raises:
            ValueError: Если цена не соответствует расчетной.
        """
        expected_price = self.item_line.price * self.quantity
        if abs(expected_price - self.line_price) > 0:
            raise ValueError(f"line_price должно быть равно {expected_price}")
        return self


class OrderSpec(BaseModel):
    """Модель заказа.

    Attributes:
        order_id: Уникальный идентификатор заказа.
        user_info: Информация о пользователе.
        items_line: Список строк заказа.

    Raises:
        ValueError: Если order_line_id не уникальны в рамках заказа.
    """

    order_id: int
    user_info: ProfileSpec
    items_line: List[OrderLineSpec]

    model_config = ConfigDict(extra="forbid")

    @model_validator(mode="after")
    def check_unique_order_lines(self):
        """Проверяет уникальность order_line_id в рамках заказа.

        Returns:
            self: Валидированный объект.

        Raises:
            ValueError: Если найдены дубликаты order_line_id.
        """
        order_line_ids = [line.order_line_id for line in self.items_line]
        if len(order_line_ids) != len(set(order_line_ids)):
            raise ValueError(
                f"order_line_id должны быть уникальными в рамках order_id={self.order_id}"
            )
        return self


class OrdersSpec(BaseModel):
    """Коллекция заказов маркетплейса.

    Attributes:
        market_place_orders: Список всех заказов.

    Raises:
        ValueError: Если нарушена уникальность идентификаторов.
    """

    market_place_orders: List[OrderSpec]

    model_config = ConfigDict(extra="forbid")

    @model_validator(mode="after")
    def check_global_uniques(self):
        """Проверяет глобальную уникальность всех идентификаторов.

        Returns:
            self: Валидированный объект.

        Raises:
            ValueError: Если найдены дубликаты идентификаторов.
        """
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
            raise ValueError("user_id должны быть уникальными")
        if len(order_ids) != len(set(order_ids)):
            raise ValueError("order_id должен быть уникальными")
        if len(item_ids) != len(set(item_ids)):
            raise ValueError("item_id должны быть уникальными")
        if len(service_ids) != len(set(service_ids)):
            raise ValueError("service_id должны быть уникальными")

        return self


def load_orders_from_yaml(file_path: str = "./data.yaml") -> Optional[OrdersSpec]:
    """Загружает и валидирует заказы из YAML файла.

    Args:
        file_path: Путь к YAML файлу с данными. По умолчанию './data.yaml'.

    Returns:
        OrdersSpec: Валидированные данные заказов или None в случае ошибки.

    Raises:
        FileNotFoundError: Если файл не найден.
        yaml.YAMLError: При ошибках парсинга YAML.
        ValidationError: При ошибках валидации данных Pydantic.

    Example:
        >>> orders = load_orders_from_yaml("data.yaml")
        >>> if orders:
        ...     print(orders.model_dump_json(indent=2))
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)

        orders = OrdersSpec(**data)
        logger.info("Данные успешно загружены и валидированы")
        return orders
    except FileNotFoundError:
        logger.error("Файл data.yaml не найден")
        return None
    except yaml.YAMLError as e:
        logger.error(f"Ошибка парсинга YAML: {e}")
        return None
    except Exception as e:
        logger.error(f"Произошла ошибка: {e}")
        return None


if __name__ == "__main__":
    """Основная точка входа при запуске скрипта.

    Загружает данные из data.yaml, валидирует их и выводит результат в JSON формате.
    """
    orders = load_orders_from_yaml()
    if orders:
        print(orders.model_dump_json(indent=2))
