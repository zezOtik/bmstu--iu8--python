from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy import select, delete, update, and_
from sqlalchemy.orm import selectinload
from typing import List, Optional

from ..models.database_models import UserOrm, BookOrm, ReadingEntryOrm
from ..models.store_models import (
    UserAdd, UserGet,
    BookAdd, BookGet,
    ReadingEntryAdd, ReadingEntryUpdate, ReadingEntryGet, ReadingEntryWithBookInfo
)


engine = create_async_engine(
    "postgresql+asyncpg://postgres:postgres@localhost:5432/postgres",
    echo=True
)
new_session = async_sessionmaker(engine, expire_on_commit=False)


class UserWorkflow:

    @classmethod
    async def add_user(cls, user: UserAdd) -> int:
        async with new_session() as session:
            new_user = UserOrm(name=user.name)
            session.add(new_user)
            await session.flush()
            await session.commit()
            return new_user.id

    @classmethod
    async def get_user_by_id(cls, user_id: int) -> Optional[UserGet]:
        async with new_session() as session:
            query = select(UserOrm).where(UserOrm.id == user_id)
            result = await session.execute(query)
            user = result.scalar_one_or_none()

            if user:
                return UserGet.model_validate(user)
            return None

    @classmethod
    async def get_all_users(cls) -> List[UserGet]:
        async with new_session() as session:
            query = select(UserOrm)
            result = await session.execute(query)
            users = result.scalars().all()

            return [UserGet.model_validate(user) for user in users]

    @classmethod
    async def delete_user(cls, user_id: int) -> bool:
        async with new_session() as session:
            query = delete(UserOrm).where(UserOrm.id == user_id)
            result = await session.execute(query)
            await session.commit()
            return result.rowcount > 0


class BookWorkflow:

    @classmethod
    async def add_book(cls, book: BookAdd) -> int:
        async with new_session() as session:
            new_book = BookOrm(
                title=book.title,
                author=book.author,
                isbn=book.isbn,
                total_pages=book.total_pages
            )
            session.add(new_book)
            await session.flush()
            await session.commit()
            return new_book.id

    @classmethod
    async def get_book_by_id(cls, book_id: int) -> Optional[BookGet]:
        async with new_session() as session:
            query = select(BookOrm).where(BookOrm.id == book_id)
            result = await session.execute(query)
            book = result.scalar_one_or_none()

            if book:
                return BookGet.model_validate(book)
            return None

    @classmethod
    async def get_all_books(cls) -> List[BookGet]:
        async with new_session() as session:
            query = select(BookOrm)
            result = await session.execute(query)
            books = result.scalars().all()

            return [BookGet.model_validate(book) for book in books]

    @classmethod
    async def get_books_by_author(cls, author: str) -> List[BookGet]:
        async with new_session() as session:
            query = select(BookOrm).where(BookOrm.author.ilike(f"%{author}%"))
            result = await session.execute(query)
            books = result.scalars().all()

            return [BookGet.model_validate(book) for book in books]

    @classmethod
    async def delete_book(cls, book_id: int) -> bool:
        async with new_session() as session:
            query = delete(BookOrm).where(BookOrm.id == book_id)
            result = await session.execute(query)
            await session.commit()
            return result.rowcount > 0


class ReadingEntryWorkflow:

    @classmethod
    async def add_reading_entry(cls, entry: ReadingEntryAdd) -> int:
        async with new_session() as session:
            book_query = select(BookOrm).where(BookOrm.id == entry.book_id)
            book_result = await session.execute(book_query)
            book = book_result.scalar_one_or_none()

            if not book:
                raise ValueError(f"Book with ID {entry.book_id} not found")

            if entry.current_page > book.total_pages:
                raise ValueError(
                    f"Current page ({entry.current_page}) cannot exceed "
                    f"total pages ({book.total_pages})"
                )

            new_entry = ReadingEntryOrm(
                book_id=entry.book_id,
                user_id=entry.user_id,
                current_page=entry.current_page
            )
            session.add(new_entry)
            await session.flush()
            await session.commit()
            return new_entry.id

    @classmethod
    async def update_reading_progress(
        cls,
        user_id: int,
        book_id: int,
        update_data: ReadingEntryUpdate
    ) -> Optional[ReadingEntryGet]:
        async with new_session() as session:
            book_query = select(BookOrm).where(BookOrm.id == book_id)
            book_result = await session.execute(book_query)
            book = book_result.scalar_one_or_none()

            if not book:
                raise ValueError(f"Book with ID {book_id} not found")

            if update_data.current_page > book.total_pages:
                raise ValueError(
                    f"Current page ({update_data.current_page}) cannot exceed "
                    f"total pages ({book.total_pages})"
                )

            query = (
                update(ReadingEntryOrm)
                .where(
                    and_(
                        ReadingEntryOrm.user_id == user_id,
                        ReadingEntryOrm.book_id == book_id
                    )
                )
                .values(
                    current_page=update_data.current_page,
                    updated_at=update_data.updated_at
                )
                .returning(ReadingEntryOrm)
            )

            result = await session.execute(query)
            await session.commit()

            updated_entry = result.scalar_one_or_none()
            if updated_entry:
                return ReadingEntryGet.model_validate(updated_entry)
            return None

    @classmethod
    async def get_reading_entries_by_user(cls, user_id: int) -> List[ReadingEntryWithBookInfo]:
        async with new_session() as session:
            query = (
                select(ReadingEntryOrm)
                .where(ReadingEntryOrm.user_id == user_id)
                .options(selectinload(ReadingEntryOrm.book))
            )
            result = await session.execute(query)
            entries = result.scalars().all()

            response = []
            for entry in entries:
                entry_with_book = ReadingEntryWithBookInfo(
                    id=entry.id,
                    book_id=entry.book_id,
                    user_id=entry.user_id,
                    current_page=entry.current_page,
                    updated_at=entry.updated_at,
                    book=BookGet.model_validate(entry.book),
                    is_finished=entry.current_page >= entry.book.total_pages
                )
                response.append(entry_with_book)

            return response

    @classmethod
    async def get_unfinished_books(cls, user_id: int) -> List[ReadingEntryWithBookInfo]:
        async with new_session() as session:
            query = (
                select(ReadingEntryOrm)
                .where(ReadingEntryOrm.user_id == user_id)
                .options(selectinload(ReadingEntryOrm.book))
            )
            result = await session.execute(query)
            entries = result.scalars().all()

            response = []
            for entry in entries:
                if entry.current_page < entry.book.total_pages:
                    entry_with_book = ReadingEntryWithBookInfo(
                        id=entry.id,
                        book_id=entry.book_id,
                        user_id=entry.user_id,
                        current_page=entry.current_page,
                        updated_at=entry.updated_at,
                        book=BookGet.model_validate(entry.book),
                        is_finished=False
                    )
                    response.append(entry_with_book)

            return response

    @classmethod
    async def get_finished_books(cls, user_id: int) -> List[ReadingEntryWithBookInfo]:
        async with new_session() as session:
            query = (
                select(ReadingEntryOrm)
                .where(ReadingEntryOrm.user_id == user_id)
                .options(selectinload(ReadingEntryOrm.book))
            )
            result = await session.execute(query)
            entries = result.scalars().all()

            response = []
            for entry in entries:
                if entry.current_page >= entry.book.total_pages:
                    entry_with_book = ReadingEntryWithBookInfo(
                        id=entry.id,
                        book_id=entry.book_id,
                        user_id=entry.user_id,
                        current_page=entry.current_page,
                        updated_at=entry.updated_at,
                        book=BookGet.model_validate(entry.book),
                        is_finished=True
                    )
                    response.append(entry_with_book)

            return response

    @classmethod
    async def delete_reading_entry(cls, user_id: int, book_id: int) -> bool:
        async with new_session() as session:
            query = delete(ReadingEntryOrm).where(
                and_(
                    ReadingEntryOrm.user_id == user_id,
                    ReadingEntryOrm.book_id == book_id
                )
            )
            result = await session.execute(query)
            await session.commit()
            return result.rowcount > 0