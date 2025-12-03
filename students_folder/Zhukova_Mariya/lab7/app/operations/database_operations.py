from app.models.database_models import AuthorOrm, PostOrm, CommentOrm
from app.models.store_models import AuthorAdd, AuthorGet, PostAdd, PostGet, CommentAdd, CommentGet, PostWithComments
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.orm import selectinload
from sqlalchemy import select
from typing import List
from datetime import datetime

from app.operations.database_migrations import engine, new_session


class BlogWorkflow:

    # создание всего
    @classmethod
    async def create_author(cls, author: AuthorAdd) -> int:
        async with new_session() as session:
            new_author = AuthorOrm(**author.model_dump())
            session.add(new_author)
            await session.commit()
            return new_author.id

    @classmethod
    async def create_post(cls, post: PostAdd) -> int:
        async with new_session() as session:

            post_data = post.model_dump()

            if post_data.get('created_at') is None:
                post_data.pop('created_at', None)
            
            new_post = PostOrm(**post_data)
            session.add(new_post)
            await session.commit()
            await session.refresh(new_post)  # Обновляем объект, чтобы получить значения из БД
            return new_post.id

    @classmethod
    async def create_comment(cls, comment: CommentAdd) -> int:
        async with new_session() as session:

            comment_data = comment.model_dump()
            if comment_data.get('created_at') is None:
                comment_data.pop('created_at', None)
            
            new_comment = CommentOrm(**comment_data)
            session.add(new_comment)
            await session.commit()
            await session.refresh(new_comment)  # Обновляем объект, чтобы получить значения из БД
            return new_comment.id

    # Получить все комменты для конкретного поста
    @classmethod
    async def get_comments_for_post(cls, post_id: int) -> List[CommentGet]:
        async with new_session() as session:
            query = select(CommentOrm).where(
                CommentOrm.post_id == post_id
            ).order_by(CommentOrm.created_at.asc())
            
            result = await session.execute(query)
            comments = result.scalars().all()
            
            return [CommentGet.model_validate(comment) for comment in comments]

    # поиск по автору
    @classmethod
    async def search_by_author(cls, author_id: int) -> List[PostGet]:
        async with new_session() as session:
            query = select(PostOrm).where(
                PostOrm.author_id == author_id
            ).order_by(PostOrm.created_at.desc())
            result = await session.execute(query)
            posts = result.scalars().all()
            
            return [PostGet.model_validate(post) for post in posts]

    # Получить всех авторов
    @classmethod
    async def get_all_authors(cls) -> List[AuthorGet]:
        async with new_session() as session:
            query = select(AuthorOrm).order_by(AuthorOrm.username)
            result = await session.execute(query)
            authors = result.scalars().all()
            
            return [AuthorGet.model_validate(author) for author in authors]

    # Получить все посты
    @classmethod
    async def get_all_posts(cls) -> List[PostGet]:
        async with new_session() as session:
            query = select(PostOrm).order_by(PostOrm.created_at.desc())
            result = await session.execute(query)
            posts = result.scalars().all()
            
            return [PostGet.model_validate(post) for post in posts]

    # Дополнительный метод: получить пост с комментариями
    @classmethod
    async def get_post_with_comments(cls, post_id: int) -> PostWithComments | None:
        async with new_session() as session:
            query = (
                select(PostOrm)
                .options(selectinload(PostOrm.comments))
                .where(PostOrm.id == post_id)
            )
            result = await session.execute(query)
            post = result.scalar_one_or_none()
            
            if post:
                # Преобразуем в Pydantic модель
                post_data = PostGet.model_validate(post)
                comments = [
                    CommentGet.model_validate(comment) 
                    for comment in post.comments
                ]
                return PostWithComments(
                    **post_data.model_dump(),
                    comments=comments
                )
            return None