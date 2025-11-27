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
