from __future__ import annotations
from dataclasses import dataclass

from recommender.data.auth.user import BasicUser


@dataclass
class DisplayableUser:
    @staticmethod
    def from_user(user: BasicUser) -> DisplayableUser:
        return DisplayableUser(
            id=user.id,
            nickname=user.nickname,
        )

    id: str
    nickname: str
