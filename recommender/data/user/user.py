from __future__ import annotations
from dataclasses import dataclass

from sqlalchemy import String, Column

from recommender.data.serializable import serializable
from recommender.db_config import DbBase


@serializable
@dataclass
class SerializableBasicUser:
    id: str
    nickname: str


@serializable
@dataclass
class SerializableFullUser(SerializableBasicUser):
    email: str
    first_name: str
    last_name: str


class BasicUser(DbBase):
    __tablename__ = "user"

    id: str = Column(String(length=36), primary_key=True)
    nickname: str = Column(String(length=100))
    type: str = Column(String(length=100))

    def to_serializable_user(self) -> SerializableBasicUser:
        return SerializableBasicUser(id=self.id, nickname=self.nickname)

    __mapper_args__ = {"polymorphic_on": "type", "polymorphic_identity": "BasicUser"}


class FullUser(BasicUser):
    email: str = Column(String(length=300), nullable=True)
    first_name: str = Column(String(length=300), nullable=True)
    last_name: str = Column(String(length=300), nullable=True)
    password: str = Column(String(length=300), nullable=True)

    def to_serializable_user(self) -> SerializableBasicUser:
        return SerializableFullUser(
            id=self.id,
            nickname=self.nickname,
            email=self.email,
            first_name=self.first_name,
            last_name=self.last_name,
        )

    __mapper_args__ = {"polymorphic_identity": "FullUser"}
