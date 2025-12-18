from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional

from operations.database_operations import (
    BookWorkflow, UserWorkflow, ReadingEntryWorkflow
)
from models.store_models import (
    BookAdd, BookGet,
    UserAdd, UserGet,
    ReadingEntryAdd, ReadingEntryUpdate, ReadingEntryWithBookInfo
)


book_router = APIRouter(
    prefix="/books",
    tags=["Книги"],
)


@book_router.post("/", response_model=BookGet, status_code=status.HTTP_201_CREATED)
async def add_book(book: BookAdd = Depends()) -> BookGet:
    try:
        book_id = await BookWorkflow.add_book(book)
        created_book = await BookWorkflow.get_book_by_id(book_id)
        return created_book
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to add book: {str(e)}"
        )


@book_router.get("/{book_id}", response_model=BookGet)
async def get_book(book_id: int) -> BookGet:
    book = await BookWorkflow.get_book_by_id(book_id)
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Book with ID {book_id} not found"
        )
    return book


@book_router.get("/", response_model=List[BookGet])
async def get_all_books() -> List[BookGet]:
    return await BookWorkflow.get_all_books()


@book_router.get("/search/author/{author_name}", response_model=List[BookGet])
async def get_books_by_author(author_name: str) -> List[BookGet]:
    return await BookWorkflow.get_books_by_author(author_name)


user_router = APIRouter(
    prefix="/users",
    tags=["Пользователи"],
)


@user_router.post("/", response_model=UserGet, status_code=status.HTTP_201_CREATED)
async def add_user(user: UserAdd = Depends()) -> UserGet:
    try:
        user_id = await UserWorkflow.add_user(user)
        created_user = await UserWorkflow.get_user_by_id(user_id)
        return created_user
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to add user: {str(e)}"
        )


@user_router.get("/{user_id}", response_model=UserGet)
async def get_user(user_id: int) -> UserGet:
    user = await UserWorkflow.get_user_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found"
        )
    return user


reading_router = APIRouter(
    prefix="/reading",
    tags=["Записи чтения"],
)


@reading_router.post("/", response_model=ReadingEntryWithBookInfo, status_code=status.HTTP_201_CREATED)
async def add_reading_entry(entry: ReadingEntryAdd = Depends()) -> ReadingEntryWithBookInfo:
    try:
        entry_id = await ReadingEntryWorkflow.add_reading_entry(entry)

        entries = await ReadingEntryWorkflow.get_reading_entries_by_user(entry.user_id)
        created_entry = next((e for e in entries if e.id == entry_id), None)

        if not created_entry:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to retrieve created reading entry"
            )

        return created_entry
    except ValueError as ve:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(ve)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to add reading entry: {str(e)}"
        )


@reading_router.put("/{user_id}/books/{book_id}", response_model=ReadingEntryWithBookInfo)
async def update_reading_progress(
    user_id: int,
    book_id: int,
    update_data: ReadingEntryUpdate = Depends()
) -> ReadingEntryWithBookInfo:
    try:
        updated_entry = await ReadingEntryWorkflow.update_reading_progress(
            user_id=user_id,
            book_id=book_id,
            update_data=update_data
        )

        if not updated_entry:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Reading entry for user {user_id} and book {book_id} not found"
            )

        entries = await ReadingEntryWorkflow.get_reading_entries_by_user(user_id)
        full_entry = next((e for e in entries if e.id == updated_entry.id), None)

        return full_entry
    except ValueError as ve:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(ve)
        )


@reading_router.get("/user/{user_id}/all", response_model=List[ReadingEntryWithBookInfo])
async def get_user_reading_entries(user_id: int) -> List[ReadingEntryWithBookInfo]:
    entries = await ReadingEntryWorkflow.get_reading_entries_by_user(user_id)
    if not entries:
        return []
    return entries


@reading_router.get("/user/{user_id}/books/unfinished", response_model=List[ReadingEntryWithBookInfo])
async def get_unfinished_books(user_id: int) -> List[ReadingEntryWithBookInfo]:
    return await ReadingEntryWorkflow.get_unfinished_books(user_id)


@reading_router.get("/user/{user_id}/books/finished", response_model=List[ReadingEntryWithBookInfo])
async def get_finished_books(user_id: int) -> List[ReadingEntryWithBookInfo]:
    return await ReadingEntryWorkflow.get_finished_books(user_id)


@reading_router.delete("/{user_id}/books/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_reading_entry(user_id: int, book_id: int):
    deleted = await ReadingEntryWorkflow.delete_reading_entry(user_id, book_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Reading entry for user {user_id} and book {book_id} not found"
        )