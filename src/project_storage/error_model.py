from __future__ import annotations

import uuid

from typing import Optional

from pydantic import BaseModel
from fastapi.encoders import jsonable_encoder


class ErrorModel(BaseModel):

    @classmethod
    def asjson(cls, **kwargs) -> ErrorModel:
        return jsonable_encoder(ErrorModel(**kwargs), exclude_unset=True)

    project_id: Optional[uuid.UUID] = None
    project_name: Optional[str] = None
    user_id: Optional[uuid.UUID] = None
    username: Optional[str] = None
    document_id: Optional[uuid.UUID] = None
    document_name: Optional[str] = None
    document_type: Optional[str] = None
    document_size: Optional[int] = None
    description: Optional[str] = None
