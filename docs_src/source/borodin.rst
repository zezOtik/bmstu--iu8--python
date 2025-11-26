Borodin
=======

Бородин Александр
-----------------

В лабораторной работе №3 реализована система валидации данных с помощью **Pydantic**.
Основная цель — создать строгую и надёжную модель данных для маркетплейса, включая:
- пользователей (`UserSpec`, `ProfileSpec`),
- товары и услуги (`ItemSpec`, `ServiceSpec`),
- заказы (`OrderLineSpec`, `OrderSpec`, `OrdersSpec`).

Все модели используют строгую валидацию:
- типы данных,
- ограничения (`gt=0` для ID и цен),
- регулярные выражения для текстовых полей (только кириллица, пробелы и дефисы),
- проверка email через `EmailStr`,
- URL-поля через `HttpUrl`,
- запрет дополнительных полей (`extra='forbid'`).

Мои модели данных:
::

    from pydantic import BaseModel, Field, ConfigDict, EmailStr
    from typing import Optional, Literal, List, Union

    class UserSpec(BaseModel):
        user_id: int = Field(gt=0)
        username: str = Field(pattern=r'^[а-яА-ЯёЁ\s\-]+$')
        surname: str = Field(pattern=r'^[а-яА-ЯёЁ\s\-]+$')
        second_name: Optional[str] = Field(None, pattern=r'^[а-яА-ЯёЁ\s\-]+$')
        email: EmailStr
        status: Literal['active', 'non-active']
        model_config = ConfigDict(extra='forbid')

    class ProfileSpec(UserSpec):
        bio: str = Field(pattern=r'^[а-яА-ЯёЁ\s\-.,!?]+$')
        url: HttpUrl
        model_config = ConfigDict(extra='forbid')

    class ItemSpec(BaseModel):
        item_id: int = Field(gt=0)
        name: str = Field(pattern=r'^[а-яА-ЯёЁ\s\-]+$')
        desc: str = Field(pattern=r'^[а-яА-ЯёЁ\s\-]+$')
        price: float = Field(gt=0)
        model_config = ConfigDict(extra='forbid')

    class ServiceSpec(BaseModel):
        service_id: int = Field(gt=0)
        name: str = Field(pattern=r'^[а-яА-ЯёЁ\s\-]+$')
        desc: str = Field(pattern=r'^[а-яА-ЯёЁ\s\-]+$')
        price: float = Field(gt=0)
        model_config = ConfigDict(extra='forbid')

    class OrderLineSpec(BaseModel):
        order_id: int
        order_line_id: int
        item_line: Union[ItemSpec, ServiceSpec]
        quantity: float = Field(gt=0)
        line_price: float = Field(gt=0)

        @model_validator(mode='after')
        def validate_line_price(self) -> 'OrderLineSpec':
            calculated = self.quantity * self.item_line.price
            if abs(self.line_price - calculated) > 1e-9:
                raise ValueError(
                    f'line_price {self.line_price} != quantity * item_line.price {calculated}'
                )
            return self

        model_config = ConfigDict(extra='forbid')

    class OrderSpec(BaseModel):
        order_id: int
        user_info: ProfileSpec
        items_line: List[OrderLineSpec]
        model_config = ConfigDict(extra='forbid')

    class OrdersSpec(BaseModel):
        market_place_orders: List[OrderSpec]
        model_config = ConfigDict(extra='forbid')

Тестирование и сборка
----------------------

- Все модели покрыты **параметризованными тестами** через `pytest`.
- Тесты запускаются с помощью **tox** в изолированном окружении.
- Для запуска тестов лабораторной работы №3 используется команда:
    .. code-block:: bash

        tox -e borodin_lab3

- Документация генерируется автоматически с помощью **Sphinx** и **sphinx-apidoc**.
- Автоматическая сборка документации настроена через **GitHub Actions**.
- Итоговая HTML-документация публикуется на **GitHub Pages**.

Структура проекта
------------------

- ``students_folder/Borodin/LabaMore1/lab_1.py`` — исходный код моделей
- ``tests/Borodin/`` — тесты с маркером ``@pytest.mark.borodin_lab3``
- ``tests/src/Borodin/lab_3/`` — YAML-файлы с тестовыми данными
- ``docs_src/`` — исходники документации (RST)
- ``docs/_build/html/`` — сгенерированная HTML-документация

Эта документация автоматически обновляется при каждом пуше в основную ветку репозитория.