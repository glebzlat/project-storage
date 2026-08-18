import uuid

from typing import Optional
from datetime import datetime

from pydantic import BaseModel, Field


class CreateProject(BaseModel):
    name: str = Field(..., min_length=1, max_length=64)
    description: Optional[str] = None


class UpdateProject(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=64)
    description: Optional[str] = None


class ExistingProject(BaseModel):
    id: uuid.UUID
    name: str
    description: Optional[str]
    created_at: datetime
    owner_id: uuid.UUID


class ExistingProjectList(BaseModel):
    n: int
    projects: list[ExistingProject]
