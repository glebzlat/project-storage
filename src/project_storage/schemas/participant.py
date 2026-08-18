import uuid

from pydantic import BaseModel


class AddParticipant(BaseModel):
    username: str


class Participant(BaseModel):
    username: str
    name: str
    uid: uuid.UUID


class ParticipantList(BaseModel):
    n: int
    participants: list[Participant]
