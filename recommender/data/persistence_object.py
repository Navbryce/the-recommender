from typing import Dict

from sqlalchemy import Column, DateTime, func


class PersistenceObject:
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), server_onupdate=func.now())

    def __repr__(self):
        return f'{self.__class__.__name__} {{{ ", ".join([f"{key}={value}" for key, value in  self.__dict__.items()])}}}'
