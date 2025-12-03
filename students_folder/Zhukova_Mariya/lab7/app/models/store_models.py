from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime


# author model
class AuthorAdd(BaseModel):  # добавить
    username: str
    bio: str | None = None


class AuthorGet(AuthorAdd):  # получить
    id: int
    model_config = ConfigDict(from_attributes=True)


# post model
class PostAdd(BaseModel):  # добавить
    title: str
    content: str
    author_id: int
    created_at: datetime | None = None


class PostGet(PostAdd):  # получить
    id: int
    created_at: datetime 
    model_config = ConfigDict(from_attributes=True)


# comment model
class CommentAdd(BaseModel):  # добавить
    content: str
    post_id: int
    author_id: int
    # Убираем default_factory здесь
    created_at: datetime | None = None


class CommentGet(CommentAdd):  # получить
    id: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


# post и comments
class PostWithComments(PostGet):  # получить комменты под постом
    comments: list[CommentGet]