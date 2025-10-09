from students_folder.Zotov_folder.lab_2.User import User
from pydantic import ConfigDict


class Profile(User):
    """Модель профиля пользователя, расширяющая базовую модель User.

    Наследует все поля и валидации от класса `User` (user_id, name, surname, age)
    и добавляет дополнительное поле `salary`.

    Атрибуты:
        salary (int): Заработная плата пользователя. Должна быть целым числом.
                      Отсутствует явная валидация в текущей реализации,
                      но может быть добавлена при необходимости.

    Конфигурация:
        extra="forbid": Запрещает передачу полей, не объявленных в модели
        (включая унаследованные от `User`). Любое неизвестное поле вызовет
        исключение `ValidationError`.

    Пример:
        >>> profile = Profile(
        ...     user_id=1,
        ...     name="Анна",
        ...     surname="Смирнова",
        ...     age=25,
        ...     salary=75000
        ... )
        >>> print(profile)
        user_id=1 name='Анна' surname='Смирнова' age=25 salary=75000

        >>> Profile(user_id=2, name="Борис", surname="Кузнецов", age=20, salary=50000, extra_field="error")
        Traceback (most recent call last):
        ...
        pydantic_core._pydantic_core.ValidationError: 1 validation error for Profile
        extra_field
          Extra inputs are not permitted [type=extra_forbidden, ...]
    """

    model_config = ConfigDict(extra="forbid")
    salary: int