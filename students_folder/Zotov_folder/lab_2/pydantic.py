from pydantic import BaseModel, ConfigDict, field_validator


class User(BaseModel):
    model_config = ConfigDict(extra='forbid')
    user_id: int
    name: str
    surname: str
    age: str

    @field_validator('age', mode='after')
    @classmethod
    def is_pos(cls, value: int) -> int:
        if value <= 18:
            raise ValueError(f'{value} младше 18')
        return value
