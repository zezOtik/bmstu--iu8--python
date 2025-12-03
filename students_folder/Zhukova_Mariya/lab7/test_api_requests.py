''' Тестовый файлик в доказательство что апи работает (честно)'''
import requests
import json
from typing import Dict, Any


BASE_URL = "http://127.0.0.1:8000"


def test_create_author(username): # создать автора
    url = f"{BASE_URL}/authors/"
    
    data = {
        "username": f'{username}',
        "bio": "Люблю писать статьи о программировании"
    }
    
    response = requests.post(url, json=data)

    print(f"Status: {response.status_code}")
    print(f"Response text: {response.text}") 
    return response

def test_get_all_authors(): 
    url = f"{BASE_URL}/authors/"
    response = requests.get(url)
    return response.json()


def test_create_post(author_id: int):
    """Тест создания поста"""
    url = f"{BASE_URL}/posts/"
    
    data = {
        "title": "Мой первый пост на FastAPI",
        "content": "Этот пост написан с помощью FastAPI и SQLAlchemy...",
        "author_id": author_id
    }
    
    response = requests.post(url, json=data)
    return response.json()

def test_get_all_posts(): 
    url = f"{BASE_URL}/posts/"
    response = requests.get(url)
    return response.json()


def test_create_comment(author_id: int, post_id: int):
    """Тест создания комментария"""
    url = f"{BASE_URL}/comments/"
    
    data = {
        "content": "Отличная статья! Очень полезно для начинающих.",
        "author_id": author_id,
        "post_id": post_id
    }
    
    response = requests.post(url, json=data)
    return response.json()


def test_get_post_comments(post_id: int):
    """Тест получения комментариев к посту"""
    url = f"{BASE_URL}/posts/{post_id}/comments"
    
    response = requests.get(url)
    return response.json()


def test_search_by_author(author_id: int):
    """Тест поиска постов по автору"""
    url = f"{BASE_URL}/posts/author/{author_id}"
    
    response = requests.get(url)
    return response.json()


def main():
    """Основная функция тестирования"""
    print(f"Тестирование API блога на {BASE_URL}")
    print(f"{'='*60}")
    
    try:
        print("1. Создаем автора")
        author_response = test_create_author(username="TEST_USER_3")
        print(author_response)

        print("2. Смотрим всех авторов")
        all_authors = test_get_all_authors()
        print(all_authors)
        
        print("3. Создаем пост автору с id 1")
        post_response = test_create_post(1)
        print(post_response)

        print("4. Получаем все посты")
        posts_response = test_get_all_posts()
        print(posts_response)

        print("5. Создаем первый комментарий автору с id 1 к посту с id 1")
        comment1_response = test_create_comment(author_id=1, post_id=1)
        print(comment1_response)
        
        print("6. Получаем комментарии к посту c id 1")
        comment2_response = test_get_post_comments(post_id=1)
        print(comment2_response)
        
        print("7. Ищем посты по автору")
        postss = test_search_by_author(1)
        print(postss)
        
        
    except requests.exceptions.ConnectionError:
        print(f"\nОШИБКА: нет подключения к {BASE_URL}")
    except Exception as e:
        print(f"\nОШИБКА: {str(e)}")

if __name__ == "__main__":
    main()