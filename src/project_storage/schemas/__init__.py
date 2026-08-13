import uuid

from typing import Optional
from datetime import datetime

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


class ExistingProject(BaseModel):
    id: uuid.UUID
    name: str
    description: Optional[str]
    created_at: datetime
    owner_id: uuid.UUID
