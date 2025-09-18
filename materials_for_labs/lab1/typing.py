from typing import Optional, Union, Any
from pydantic import BaseModel


class User(BaseModel):
    name: Optional[str]
    surname: str


class User2(BaseModel):
    name: Any


class User3(BaseModel):
    name: Union[str, int]


test_User = User(name=None, surname="Testov")
test_User2 = User2(name=123)
test_User3 = User2(name="Vasya")
test_User4 = User3(name=123)
test_User5 = User3(name="Lololo")
print(test_User2)
print(test_User3)
print(test_User4)
print(test_User5)
