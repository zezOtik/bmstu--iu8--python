### Пример одного метода для API

1) Настройка виртуального окружения

```commandline
python3 -m venv .venv
```

2) Активация виртуального окружения

```commandline
source .venv/bin/activate
```

3) Установка python зависимостей

```
pip install -r requirements.txt
```
4) Создаем основной файл

```commandline
mkdir ./app
touch ./app/main.py
```

5) В нем(main.py) создадим один простой endpoint c выводом "Hello world"

```
from fastapi import FastAPI

app = FastAPI()
@app.get("/")

async def main():
   return {"data": "Hello World"}
```

6) Запустим наш веб-сервер с этим методом, проверим работоспособность FastAPI и uvicorn(--reload для того, чтобы сразу подтягивать изменения в коде)

```commandline
uvicorn app.main:app --reload
```

7) Перейдите на http://127.0.0.1:8000/docs и испытайте свой первый метод.

8) Теперь создадим модель для API метода. Добавим папку ./models и файл store_models.py
```commandline
mkdir -p ./app/models && touch ./app/models/store_models.py
```

9) Тут как и в прошлых лабораторных работах, надо сделать классы для ваших потребностей
Для начала создадим класс описывающий заказы и модель для метода создания заказа в файле store_models.py

```python
from pydantic import BaseModel, AfterValidator, Field
from typing import Annotated, Literal
from datetime import datetime
from zoneinfo import ZoneInfo


def validate_aware(dt: datetime) -> datetime:
    if dt.tzinfo is None:
        raise ValueError("datetime must include timezone information")
    return dt


AwareDatetime = Annotated[datetime, AfterValidator(validate_aware)]


def default_execution_time():
    return datetime.now(ZoneInfo("UTC"))


class OrderBase(BaseModel):
    id: int
    customer_id: int
    desc: str | None = None
    created_at: AwareDatetime = Field(default_factory=default_execution_time)
    status: Literal['new', 'delivery', 'finished']


class OrderAdd(OrderBase):
    pass
```

10) Теперь нужно подтянуть эти модели в API, т.е. в наш main.py, файл будет выглядеть следующим образом

```python
from fastapi import FastAPI
from app.models.store_models import OrderAdd

app = FastAPI()

@app.get("/")
async def main():
   return {"data": "Hello World"}

@app.post("/add_order")
async def add_order(order: OrderAdd):
   return {"data": order}
```

11) Как видите, у нас теперь появился метод по добавлению задачи, в который нужно передать dict(),
который валидируется Pydantic моделью.

12) Для того, чтобы использовать всю "мощь" связки Pydantic и FastApi, добавим
```python
from fastapi import Depends
```
И main.py будет выглядеть следующим образом
```python
from fastapi import FastAPI, Depends
from app.models.store_models import OrderAdd

app = FastAPI()

@app.get("/")
async def main():
   return {"data": "Hello World"}

@app.post("/add_order")
async def add_order(order: OrderAdd = Depends()):
   return {"data": order}
```
теперь в http://127.0.0.1:8000/docs вы увидите на UI, что идет передача информации о том, какие атрибуты обязательные и т.п.

13) Перейдем к настройке работы с БД. Заранее добавим директории для операций с БД
```commandline
mkdir ./app/operations
touch ./app/operations/database_operations.py
```
14) Также нам необходимы ORM(https://blog.skillfactory.ru/glossary/orm/) модели для работы с БД, поэтому добавим модели для этого
```commandline
touch ./app/models/database_models.py
```
15) Создадим ORM модель в ./app/models/database_models.py
```python
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import DateTime, BIGINT
from datetime import datetime
from zoneinfo import ZoneInfo


def utc_now() -> datetime:
    return datetime.now(ZoneInfo("UTC"))


class TableModel(DeclarativeBase):
    pass


class OrderOrm(TableModel):
    __tablename__ = "order"
    __table_args__ = {"schema": "public"}

    id: Mapped[int] = mapped_column(BIGINT, primary_key=True, autoincrement=True)
    customer_id: Mapped[int]
    desc: Mapped[str | None]
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now
    )
    status: Mapped[str] = mapped_column(
        default='new'
    )

```

16) Напишем функции для работы с Postgresql для этого создадим методы в ./app/operations/database_operations.py
```python
from app.models.database_models import OrderOrm
from app.models.store_models import OrderAdd, OrderListGet
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy import select
from typing import List


engine = create_async_engine("postgresql+asyncpg://postgres:postgres@localhost:5432/postgres")
new_session = async_sessionmaker(engine, expire_on_commit=False)


class OrderWorkflow:
    @classmethod
    async def add_order(cls, order: OrderAdd) -> int:
        async with new_session() as session:
            data = order.model_dump()
            new_order = OrderOrm(**data)
            session.add(new_order)
            await session.flush()
            await session.commit()
            return new_order.id

    @classmethod
    async def get_orders(cls) -> OrderListGet:
        async with new_session() as session:
            query = select(OrderOrm)
            result = await session.execute(query)
            order_models = result.scalars().all()

            orders = OrderListGet.model_validate(order_models)
            return orders.root

```

17) На самом деле нам лучше еще обновить модели изначальные, так как мы не хотим в ручную указывать id при создание, т.к. ORM модель сама это может делать за нас. Обновим Pydantic модели.
Дополнительно обновим модель вывода всех заказов.
```python
from pydantic import BaseModel, AfterValidator, Field, ConfigDict, RootModel
from typing import Annotated, Literal, Optional, List
from datetime import datetime
from zoneinfo import ZoneInfo


def validate_aware(dt: datetime) -> datetime:
    if dt.tzinfo is None:
        raise ValueError("datetime must include timezone information")
    return dt


AwareDatetime = Annotated[datetime, AfterValidator(validate_aware)]

def default_execution_time():
    return datetime.now(ZoneInfo("UTC"))


class OrderBase(BaseModel):
    customer_id: int
    desc: str | None = None
    created_at: Optional[AwareDatetime] = Field(default_factory=default_execution_time)
    status: Literal['new', 'delivery', 'finished']


class OrderAdd(OrderBase):
    pass


class OrderGet(OrderBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


class OrderListGet(RootModel[List[OrderGet]]):
    model_config = ConfigDict(from_attributes=True)

```
18) Но прежде, чем идти и запускать, у нас не настроены же таблицы в базе, т.е. их нужно создать и удалять, если модель пока у нас меняется. Создадим файл миграций таблицы
```commandline
touch ./app/opeartions/database_migartions.py
```
В нем опишем наши миграции
```python
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from app.models.database_models import TableModel

engine = create_async_engine("postgresql+asyncpg://postgres:postgres@localhost:5432/postgres")

async def create_table():
   async with engine.begin() as conn:
       await conn.run_sync(TableModel.metadata.create_all)

async def delete_table():
   async with engine.begin() as conn:
       await conn.run_sync(TableModel.metadata.drop_all)
```

18) Теперь надо навести порядок, как видите у нас появились почти все методы для orders, надо настроить роутер для облегчения работы с endpoint.
```commandline
touch ./app/router_order.py
```
```python
from fastapi import APIRouter, Depends

from app.operations.database_operations import OrderWorkflow
from app.models.store_models import OrderAdd, OrderGet

from typing import List


router = APIRouter(
    prefix="/orders",
    tags=["Заказы"],
)

@router.post(
    "/add_order",
    summary="Добавление нового заказа")
async def add_order(order: OrderAdd = Depends()) -> dict:
    id = await OrderWorkflow.add_order(order)
    return {"id": id}

@router.get("/get_orders",
            summary="Получение заказов")
async def get_orders() -> List[OrderGet]:
    orders = await OrderWorkflow.get_orders()
    return orders

```

19) Ну, конечно, надо обновить main.py теперь и добавить накатку таблиц при перезапуске:
```python
from app.operations.database_migrations import create_table, delete_table

from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.router_order import router as orders_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_table()
    print("Таблица готова")
    yield
    await delete_table()
    print("Таблица очищена")


app = FastAPI(lifespan=lifespan)

app.include_router(orders_router)
```


Полезные вещи если порты заняты
```commandline
 lsof -i :8000
 kill -9 pid # то что в ответе у вас
```
