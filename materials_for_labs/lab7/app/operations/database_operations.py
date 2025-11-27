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
