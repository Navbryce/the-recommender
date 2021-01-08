import os
from typing import Optional
from uuid import uuid4

from recommender.data.user.user import (
    BasicUser,
    SerializableFullUser,
    SerializableBasicUser,
)
from recommender.db_config import DbSession


class UserManager:
    def create_anonymous_user_and_generate_name(self) -> BasicUser:
        return self.create_anonymous_user(self.generate_user_name())

    def generate_user_name(self) -> str:
        return str(uuid4())

    def create_anonymous_user(self, nickname: str) -> BasicUser:
        user_id = str(uuid4())
        user: BasicUser = BasicUser(id=user_id, nickname=nickname)
        db_session = DbSession()
        db_session.add(user)
        db_session.commit()

        return user

    def get_user(self, email: str, password: str) -> Optional[SerializableBasicUser]:
        # Hard code in admin account
        if email == os.environ["ADMIN_EMAIL"] and password == os.environ["ADMIN_PASS"]:
            return SerializableFullUser(
                id="Admin",
                nickname="Admin",
                first_name="Admin",
                last_name="Admin",
                email=os.environ["ADMIN_EMAIL"],
                is_admin=True,
            )
        return None
