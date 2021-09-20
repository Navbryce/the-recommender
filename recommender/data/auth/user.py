from __future__ import annotations

from collections import Callable
from dataclasses import dataclass, field

from sqlalchemy import String, Column, Boolean, CheckConstraint
from sqlalchemy.orm import Session, Query, validates

from recommender.db_config import DbBase


@dataclass
class SerializableBasicUser:
    id: str
    nickname: str
    is_admin: bool

    def __init__(self, id: str, nickname: str, is_admin: bool = False):
        self.id = id
        self.nickname = nickname
        self.is_admin = is_admin

    def __getstate__(self):
        return {
            **self.__dict__,
            "type": self.__class__.__name__
        }


@dataclass
class SerializableFullUser(SerializableBasicUser):
    email: str
    first_name: str
    last_name: str


class BasicUser(DbBase):
    @staticmethod
    def get_user_by_id(
            db_session: Session,
            id: str,
            query_modifier: Callable[[Query], Query] = lambda x: x,
    ) -> BasicUser:
        return query_modifier(db_session.query(BasicUser)).filter_by(id=id).first()

    __tablename__ = "user"

    id: str = Column(String(length=36), primary_key=True)
    nickname: str = Column(String(length=100), nullable=False)
    type: str = Column(String(length=100) , nullable=False)

    def to_serializable_user(self) -> SerializableBasicUser:
        return SerializableBasicUser(id=self.id, nickname=self.nickname)

    __mapper_args__ = {"polymorphic_on": "type", "polymorphic_identity": "BasicUser"}
    __table_args__ = (CheckConstraint("LENGTH(nickname) > 0"),)

    @validates("nickname")
    def validate_nickname(self, key: str, value: str):
        if len(value) == 0:
            raise ValueError("Nickname too short")
        return value


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
