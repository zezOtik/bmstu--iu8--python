"""
Тесты для основного модуля приложения.
"""
import pytest
from main import DataManager


class TestDataManager:
    """Тесты для менеджера данных."""

    @pytest.fixture
    def manager(self):
        """Для создания менеджера данных."""
        return DataManager()

    def test_create_user_and_project(self, manager):
        """Тест создания пользователя и проекта через менеджер."""
        user = manager.create_user("Test User", "test@example.com")
        project = manager.create_project("Test Project")

        assert user.name == "Test User"
        assert project.name == "Test Project"
        assert len(manager.users) == 1
        assert len(manager.projects) == 1

    def test_add_user_to_project(self, manager):
        """Тест добавления пользователя в проект."""
        user = manager.create_user("Test User", "test@example.com")
        project = manager.create_project("Test Project")

        manager.add_user_to_project(user.id, project.id)

        assert len(project.users) == 1
        assert project.users[0] == user


def test_integration():
    """Интеграционный тест полного workflow."""
    manager = DataManager()

    user1 = manager.create_user("User 1", "user1@example.com")
    user2 = manager.create_user("User 2", "user2@example.com")
    project = manager.create_project("Test Project")

    manager.add_user_to_project(user1.id, project.id)
    manager.add_user_to_project(user2.id, project.id)

    assert len(manager.users) == 2
    assert len(manager.projects) == 1
    assert len(project.users) == 2