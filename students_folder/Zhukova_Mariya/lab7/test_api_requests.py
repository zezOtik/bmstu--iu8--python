''' Тестовый файлик в доказательство что апи работает (честно)'''
import requests
import json
import yaml
from typing import Dict, Any
from pathlib import Path

BASE_URL = "http://127.0.0.1:8000"

# Загрузка тестовых данных из YAML
def load_test_data():
    with open('students_folder/Zhukova_Mariya/lab7/test_data.yaml', 'r', encoding='utf-8') as file:
        return yaml.safe_load(file)

TEST_DATA = load_test_data()

def test_create_author(author_key="test_author_1"):
    """Создание автора"""
    url = f"{BASE_URL}/authors/"
    author_data = TEST_DATA['authors'][author_key]
    
    # ⬇⬇⬇ ВАЖНО: params вместо json
    response = requests.post(url, params=author_data)
    print(f"Создание автора {author_key}: Status {response.status_code}")
    return response

def test_get_all_authors():
    """Получение всех авторов"""
    url = f"{BASE_URL}/authors/"
    response = requests.get(url)
    return response.json()

def test_create_post(author_id: int, post_key="test_post_1"):
    """Создание поста"""
    url = f"{BASE_URL}/posts/"
    
    post_data = TEST_DATA['posts'][post_key].copy()
    post_data["author_id"] = author_id
    
    # ⬇⬇⬇ params вместо json
    response = requests.post(url, params=post_data)
    print(f"Создание поста {post_key}: Status {response.status_code}")
    return response.json()

def test_get_all_posts():
    """Получение всех постов"""
    url = f"{BASE_URL}/posts/"
    response = requests.get(url)
    return response.json()

def test_create_comment(author_id: int, post_id: int, comment_key="test_comment_1"):
    """Создание комментария"""
    url = f"{BASE_URL}/comments/"
    
    comment_data = TEST_DATA['comments'][comment_key].copy()
    comment_data["author_id"] = author_id
    comment_data["post_id"] = post_id
    
    # ⬇⬇⬇ params вместо json
    response = requests.post(url, params=comment_data)
    print(f"Создание комментария {comment_key}: Status {response.status_code}")
    return response.json()

def test_get_post_comments(post_id: int):
    """Получение комментариев к посту"""
    url = f"{BASE_URL}/posts/{post_id}/comments"
    response = requests.get(url)
    return response.json()

def test_search_by_author(author_id: int):
    """Поиск постов по автору"""
    url = f"{BASE_URL}/posts/author/{author_id}"
    response = requests.get(url)
    return response.json()

def run_full_test_flow():
    """Полный поток тестирования с использованием YAML данных"""
    print(f"Тестирование API блога на {BASE_URL}")
    print(f"{'='*60}")
    
    try:
        # Тест 1: Создание автора
        print("1. Создаем автора из YAML данных")
        author_response = test_create_author("test_author_1")
        
        # Тест 2: Получение всех авторов
        print("\n2. Получаем всех авторов")
        all_authors = test_get_all_authors()
        print(f"Найдено авторов: {len(all_authors)}")
        
        # Тест 3: Создание поста
        print("\n3. Создаем пост")
        if all_authors and len(all_authors) > 0:
            author_id = all_authors[0].get('id', 1)
            post_response = test_create_post(author_id, "test_post_1")
            post_id = post_response.get('id', 1)
        
        # Тест 4: Получение всех постов
        print("\n4. Получаем все посты")
        posts_response = test_get_all_posts()
        print(f"Найдено постов: {len(posts_response)}")
        
        # Тест 5: Создание комментария
        print("\n5. Создаем комментарий")
        comment_response = test_create_comment(author_id, post_id, "test_comment_1")
        
        # Тест 6: Получение комментариев к посту
        print("\n6. Получаем комментарии к посту")
        comments_response = test_get_post_comments(post_id)
        print(f"Найдено комментариев: {len(comments_response)}")
        
        # Тест 7: Поиск постов по автору
        print("\n7. Ищем посты по автору")
        author_posts = test_search_by_author(author_id)
        print(f"Автор {author_id} имеет постов: {len(author_posts)}")
        
        print(f"\n{'='*60}")
        print("Все тесты выполнены успешно!")
        
    except requests.exceptions.ConnectionError:
        print(f"\nОШИБКА: нет подключения к {BASE_URL}")
    except KeyError as e:
        print(f"\nОШИБКА: отсутствует тестовые данные для ключа {e}")
    except Exception as e:
        print(f"\nОШИБКА: {str(e)}")

if __name__ == "__main__":
    run_full_test_flow()
