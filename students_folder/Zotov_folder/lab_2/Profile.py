from students_folder.Zotov_folder.lab_2.User import User
from pydantic import ConfigDict

class Profile(User):
    model_config = ConfigDict(extra="forbid")
    salary: int