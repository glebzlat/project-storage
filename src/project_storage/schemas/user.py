import uuid

from pydantic import BaseModel, Field


class Token(BaseModel):
    access_token: str
    token_type: str


class RegisterUser(BaseModel):
    username: str = Field(..., max_length=32)
    name: str = Field(..., max_length=64)
    password: str
    repeat_password: str


class RegisteredUser(BaseModel):
    id: uuid.UUID
    username: str
