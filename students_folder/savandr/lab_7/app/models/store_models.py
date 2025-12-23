from pydantic import BaseModel, AfterValidator, Field, ConfigDict, RootModel
from typing import Annotated, Optional, List
from datetime import datetime
from zoneinfo import ZoneInfo


def validate_aware(dt: datetime) -> datetime:
    if dt.tzinfo is None:
        raise ValueError("datetime must include timezone information")
    return dt


AwareDatetime = Annotated[datetime, AfterValidator(validate_aware)]


def default_utc_time() -> datetime:
    return datetime.now(ZoneInfo("UTC"))


class UserBase(BaseModel):
    name: str = Field(description="Имя пользователя")


class UserAdd(UserBase):
    pass


class UserGet(UserBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


class BookBase(BaseModel):
    title: str = Field(description="Название книги")
    author: str = Field(description="Автор книги")
    isbn: Optional[str] = Field(None, description="ISBN код книги")
    total_pages: int = Field(gt=0, description="Общее количество страниц в книге")


class BookAdd(BookBase):
    pass


class BookGet(BookBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


class ReadingEntryBase(BaseModel):
    book_id: int = Field(description="ID книги")
    user_id: int = Field(description="ID пользователя")
    current_page: int = Field(ge=0, description="Текущая страница чтения")
    updated_at: Optional[AwareDatetime] = Field(
        default_factory=default_utc_time,
        description="Дата последнего обновления прогресса чтения"
    )


class ReadingEntryAdd(ReadingEntryBase):
    pass


class ReadingEntryUpdate(BaseModel):
    current_page: int = Field(ge=0, description="Текущая страница чтения")
    updated_at: Optional[AwareDatetime] = Field(
        default_factory=default_utc_time,
        description="Дата обновления прогресса чтения"
    )


class ReadingEntryGet(ReadingEntryBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


class ReadingEntryWithBookInfo(ReadingEntryGet):
    book: BookGet
    is_finished: bool = Field(description="Прочитана ли книга полностью")


class BookListGet(RootModel[List[BookGet]]):
    model_config = ConfigDict(from_attributes=True)


class ReadingEntryListGet(RootModel[List[ReadingEntryWithBookInfo]]):
    model_config = ConfigDict(from_attributes=True)


class UserListGet(RootModel[List[UserGet]]):
    model_config = ConfigDict(from_attributes=True)
