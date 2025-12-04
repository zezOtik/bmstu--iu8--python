from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, DateTime, String, Text, BIGINT
from sqlalchemy.dialects.postgresql import VARCHAR
from typing import List
from datetime import datetime

# ORM - oblective relation model - крч переводит питон в sql
# тут создаются модели таблиц

class TableModel(DeclarativeBase): # базовый класс для наследования всеми остальными, его импортируем в другие файлики
    pass


class AuthorOrm(TableModel):
    __tablename__ = "author" # класс соответсвует таблице author в бд
    __table_args__ = {"schema": "public"}

    id: Mapped[int] = mapped_column(BIGINT, primary_key=True, autoincrement=True) 

    # Mapped[int] - поле типа int
    # mapped_column(BIGINT - колонка типа BIGINT - 8 байт
    # primary_key=True - первичный ключ таблицы (id каждой записи)
    # autoincrement=True — автоинкремент: БД сама увеличивает значение при вставке новых записей

    username: Mapped[str] = mapped_column(VARCHAR(50), unique=True, nullable=False)
    bio: Mapped[str | None] = mapped_column(Text)

    # связи
    posts: Mapped[List["PostOrm"]] = relationship(back_populates="author", cascade="all, delete-orphan") # связь с таблицей posts
    # у автора есть атрибут posts - список объектов PostsOrm
    # отношение 1 ко многим - 1 автор - много постов
    # cascade="all, delete-orphan" — правила каскадных операций - all - все операции связаны (автор удаляется - его посты тоже),delete-orphan — если пост убрать из списка author.posts, он будет удален из БД


class PostOrm(TableModel):
    __tablename__ = "post"
    __table_args__ = {"schema": "public"}

    id: Mapped[int] = mapped_column(BIGINT, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    author_id: Mapped[int] = mapped_column(ForeignKey("public.author.id"))


    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        default=datetime.utcnow,  # Текущее время UTC при создании
        nullable=False
    )
    
    # Связи
    author: Mapped["AuthorOrm"] = relationship(back_populates="posts")# у поста есть атрибут автор
    comments: Mapped[List["CommentOrm"]] = relationship(back_populates="post", cascade="all, delete-orphan") # у поста есть атрибут комментарии


class CommentOrm(TableModel):
    __tablename__ = "comment"
    __table_args__ = {"schema": "public"}

    id: Mapped[int] = mapped_column(BIGINT, primary_key=True, autoincrement=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    post_id: Mapped[int] = mapped_column(ForeignKey("public.post.id"))
    author_id: Mapped[int] = mapped_column(ForeignKey("public.author.id"))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        default=datetime.utcnow,  # Текущее время UTC при создании
        nullable=False
    )
    
    # Связи
    post: Mapped["PostOrm"] = relationship()
    author: Mapped["AuthorOrm"] = relationship()