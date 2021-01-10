from __future__ import annotations
from dataclasses import dataclass, field

from sqlalchemy import String, Column, Boolean

from recommender.data.serializable import serializable
from recommender.db_config import DbBase


@serializable
@dataclass
class SerializableBasicUser:
    id: str
    nickname: str
    is_admin: bool

    def __init__(self, id: str, nickname: str, is_admin: bool = False):
        self.id = id
        self.nickname = nickname
        self.is_admin = is_admin


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
    email: str = Column(String(length=300))
    first_name: str = Column(String(length=300))
    last_name: str = Column(String(length=300))
    password: str = Column(String(length=300))
    is_admin: str = Column(Boolean, default=False)

    def to_serializable_user(self) -> SerializableBasicUser:
        return SerializableFullUser(
            id=self.id,
            nickname=self.nickname,
            email=self.email,
            first_name=self.first_name,
            last_name=self.last_name,
            is_admin=self.is_admin,
        )

    __mapper_args__ = {"polymorphic_identity": "FullUser"}
