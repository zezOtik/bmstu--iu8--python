"""
Тесты для моделей данных.
"""
import pytest
from src.models import User, Project


class TestUserModel:
    """Тесты для модели User."""

    def test_user_creation_and_info(self):
        """Тест создания пользователя и метода get_info."""
        user = User(id=1, name="Test User", email="test@example.com", age=25)

        assert user.id == 1
        assert user.name == "Test User"
        assert user.email == "test@example.com"

        info = user.get_info()
        assert "Test User" in info
        assert "test@example.com" in info

    def test_anonymous_user_creation(self):
        """Тест создания анонимного пользователя."""
        anonymous = User.create_anonymous()

        assert anonymous.id == 0
        assert anonymous.name == "Anonymous"
        assert anonymous.email == "anonymous@example.com"


class TestProjectModel:
    """Тесты для модели Project."""

    def test_project_creation_and_add_user(self):
        """Тест создания проекта и добавления пользователя."""
        project = Project(id=1, name="Test Project")
        user = User(id=1, name="Test User", email="test@example.com")

        project.add_user(user)

        assert project.name == "Test Project"
        assert len(project.users) == 1
        assert project.users[0] == user