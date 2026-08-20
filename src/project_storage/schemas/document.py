import uuid

from pydantic import BaseModel


class CreatedDocument(BaseModel):
    project_id: uuid.UUID
    file_id: uuid.UUID
    file_name: str
    file_size: int


class CreatedDocumentList(BaseModel):
    n: int
    documents: list[CreatedDocument]
