from pydantic import BaseModel, ConfigDict, field_validator


class User(BaseModel):
    """Модель пользователя с валидацией возраста.

    Атрибуты:
        user_id (int): Уникальный идентификатор пользователя.
        name (str): Имя пользователя.
        surname (str): Фамилия пользователя.
        age (int): Возраст пользователя. Должен быть строго больше 18.

    Конфигурация:
        extra="forbid": Запрещает передачу дополнительных полей,
        не объявленных в модели. При попытке передать неизвестное
        поле будет вызвано исключение ValidationError.

    Валидация:
        Поле `age` проходит кастомную валидацию через метод `is_pos`.
        Если значение возраста меньше или равно 18, выбрасывается
        исключение ValueError с соответствующим сообщением.

    Пример:
        >>> user = User(user_id=1, name="Иван", surname="Иванов", age=25)
        >>> print(user)
        user_id=1 name='Иван' surname='Иванов' age=25

        >>> User(user_id=2, name="Петр", surname="Петров", age=16)
        Traceback (most recent call last):
        ...
        pydantic_core._pydantic_core.ValidationError: 1 validation error for User
        age
          16 младше 18 [type=value_error, input_value=16, input_type=int]
    """

    model_config = ConfigDict(extra="forbid")
    user_id: int
    name: str
    surname: str
    age: int

    @field_validator("age", mode="after")
    @classmethod
    def is_pos(cls, value: int) -> int:
        """Проверяет, что возраст пользователя строго больше 18.

        Args:
            value (int): Значение возраста для валидации.

        Returns:
            int: Валидное значение возраста.

        Raises:
            ValueError: Если возраст меньше или равен 18.
        """
        if value <= 18:
            raise ValueError(f"{value} младше 18")
        return value
