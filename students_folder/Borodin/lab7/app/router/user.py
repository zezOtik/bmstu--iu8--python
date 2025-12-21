from fastapi import APIRouter, Depends
from app.models.store_models import UserCreate, UserGet
from app.operations.user_ops import create_user, update_user, get_user

router = APIRouter(prefix="/users", tags=["users"])

@router.post("/", response_model=UserGet)
async def create_new_user(user: UserCreate):
    return await create_user(user)

@router.put("/{user_id}", response_model=UserGet)
async def update_existing_user(user_id: int, user: UserCreate):
    return await update_user(user_id, user)

@router.get("/{user_id}", response_model=UserGet)
async def read_user(user_id: int):
    return await get_user(user_id)