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
touch main.py
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
uvicorn main:app --reload
```

7) Перейдите на http://127.0.0.1:8000/docs и испытайте свой первый метод.

8) Теперь создадим модель для API метода. Добавим папку ./models и файл store_models.py
```commandline
mkdir -p ./models && touch ./models/store_models.py
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
from models.store_models import OrderAdd

app = FastAPI()

@app.get("/")
async def main():
   return {"data": "Hello World"}

@app.post("/add_order")
async def add_order(order: OrderAdd):
   return {"data": order}
```
