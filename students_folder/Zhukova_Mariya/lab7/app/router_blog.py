from fastapi import APIRouter, HTTPException
from app.operations.database_operations import BlogWorkflow
from app.models.store_models import PostAdd, PostWithComments, AuthorAdd, CommentAdd, CommentGet
from typing import List

router = APIRouter()


# создание автора поста
@router.post("/authors/", summary="Создание нового автора")
async def create_author(author: AuthorAdd) -> dict:
    try:
        author_id = await BlogWorkflow.create_author(author)
        return {"id": author_id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# создание поста
@router.post("/posts/", summary="Создание нового поста")
async def create_post(post: PostAdd) -> dict:
    try:
        post_id = await BlogWorkflow.create_post(post)
        return {"id": post_id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# создание коммента
@router.post("/comments/", summary="Добавление комментария к посту")
async def create_comment(comment: CommentAdd) -> dict:
    try:
        comment_id = await BlogWorkflow.create_comment(comment)
        return {"id": comment_id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# Получаем комментарии к конкретному посту по id
@router.get("/posts/{post_id}/comments", summary="Получение комментариев к посту по id")
async def get_post_comments(post_id: int):
    comments = await BlogWorkflow.get_comments_for_post(post_id)
    return comments


# поиск по автору
@router.get("/posts/author/{author_id}", summary="Поиск постов по автору")
async def search_by_author(author_id: int) -> dict:
    posts = await BlogWorkflow.search_by_author(author_id)
    return {"author_id": author_id, "posts": posts}


# получить всех авторов
@router.get("/authors/", summary="Получить всех авторов")
async def get_all_authors():
    """Получить список всех авторов"""
    authors = await BlogWorkflow.get_all_authors()
    return authors


# получить все посты
@router.get("/posts/", summary="Получить все посты")
async def get_all_posts():
    """Получить список всех постов (без комментариев)"""
    posts = await BlogWorkflow.get_all_posts()
    return posts

