from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import DateTime, BIGINT, String, ForeignKey, Integer
from datetime import datetime
from zoneinfo import ZoneInfo


def utc_now() -> datetime:
    return datetime.now(ZoneInfo("UTC"))


class TableModel(DeclarativeBase):
    pass


class UserOrm(TableModel):
    __tablename__ = "user"
    __table_args__ = {"schema": "public"}

    id: Mapped[int] = mapped_column(BIGINT, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)

    reading_entries: Mapped[list["ReadingEntryOrm"]] = relationship(
        "ReadingEntryOrm",
        back_populates="user",
        cascade="all, delete-orphan"
    )


class BookOrm(TableModel):
    __tablename__ = "book"
    __table_args__ = {"schema": "public"}

    id: Mapped[int] = mapped_column(BIGINT, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    author: Mapped[str] = mapped_column(String(255), nullable=False)
    isbn: Mapped[str | None] = mapped_column(String(20), nullable=True)
    total_pages: Mapped[int] = mapped_column(Integer, nullable=False)

    reading_entries: Mapped[list["ReadingEntryOrm"]] = relationship(
        "ReadingEntryOrm",
        back_populates="book",
        cascade="all, delete-orphan"
    )


class ReadingEntryOrm(TableModel):
    __tablename__ = "reading_entry"
    __table_args__ = {"schema": "public"}

    id: Mapped[int] = mapped_column(BIGINT, primary_key=True, autoincrement=True)
    book_id: Mapped[int] = mapped_column(BIGINT, ForeignKey("public.book.id"), nullable=False)
    user_id: Mapped[int] = mapped_column(BIGINT, ForeignKey("public.user.id"), nullable=False)
    current_page: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        nullable=False
    )

    book: Mapped["BookOrm"] = relationship("BookOrm", back_populates="reading_entries")
    user: Mapped["UserOrm"] = relationship("UserOrm", back_populates="reading_entries")
