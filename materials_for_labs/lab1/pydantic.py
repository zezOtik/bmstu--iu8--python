# -*- coding: utf-8 -*-
# https://docs.pydantic.dev/2.11/
from pydantic import BaseModel, field_validator, model_validator, ValidationError
from typing_extensions import Self
import re


class User(BaseModel):
    name: str
    surname: str

test_user = User(name="Петя", surname="Петров")

print(test_user)

class Profile(User):
    deperment_id: int

    @field_validator('deperment_id', mode='after')
    @classmethod
    def is_pos(cls, value: int) -> int:
        if value <= 0:
            raise ValueError(f'{value} is not a positive number')
        return value
    
    @model_validator(mode="after")
    def not_int_in_fio(self) -> Self:
        russian_pattern = re.compile(r'^[а-яА-ЯёЁ\s]+$')

        # for field_name in ['name', 'surname']:
        #     value = getattr(self, field_name)
        #     if not russian_pattern.match(value):
        #         raise ValueError(
        #             f'Поле "{field_name}" должно содержать только русские буквы и пробелы. '
        #             f'Получено: {value!r}'
        #         )
        
        if not russian_pattern.match(self.name) or not russian_pattern.match(self.surname):
            raise ValueError(
                    'Поле должно содержать только русские буквы и пробелы. '
                )

    
test_profile = Profile(deperment_id=12, **test_user.model_dump())
print(test_profile)

try:
    test_profile = Profile(deperment_id=10, **test_user.model_dump())
except ValidationError as err:
    print(err)



