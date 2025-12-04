"""
Модуль с моделями данных для лабораторной работы.
"""

from pydantic import BaseModel, Field
from typing import Optional, List


class User(BaseModel):
    """
    Модель пользователя системы.

    Attributes:
        id: Уникальный идентификатор пользователя
        name: Имя пользователя
        email: Электронная почта
        age: Возраст пользователя
    """

    id: int
    name: str = Field(..., description="Полное имя пользователя")
    email: str = Field(..., description="Email адрес")
    age: Optional[int] = Field(None, description="Возраст пользователя")

    def get_info(self) -> str:
        """
        Получить информацию о пользователе.

        Returns:
            Строка с информацией о пользователе

        Examples:
            >>> user = User(id=1, name="John", email="john@example.com")
            >>> user.get_info()
            'User John (john@example.com)'
        """
        return f"User {self.name} ({self.email})"

    @classmethod
    def create_anonymous(cls) -> 'User':
        """
        Создать анонимного пользователя.

        Returns:
            Экземпляр User с предустановленными значениями
        """
        return cls(
            id=0,
            name="Anonymous",
            email="anonymous@example.com",
            age=None
        )


class Project(BaseModel):
    """
    Модель проекта.

    Attributes:
        id: Уникальный идентификатор проекта
        name: Название проекта
        description: Описание проекта
        users: Список пользователей проекта
        is_active: Статус активности проекта
    """

    id: int
    name: str
    description: Optional[str] = None
    users: List[User] = []
    is_active: bool = True

    def add_user(self, user: User) -> None:
        """
        Добавить пользователя в проект.

        Args:
            user: Объект пользователя для добавления

        Raises:
            ValueError: Если пользователь уже в проекте
        """
        if user in self.users:
            raise ValueError("User already in project")
        self.users.append(user)

    def get_active_users(self) -> List[User]:
        """
        Получить список пользователей проекта.

        Returns:
            Список объектов User
        """
        return [user for user in self.users]