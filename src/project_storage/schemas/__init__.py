from typing import Optional

from pydantic import BaseModel


class User(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class CreateProject(BaseModel):
    name: str
    description: Optional[str]
