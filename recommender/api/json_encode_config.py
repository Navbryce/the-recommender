from enum import Enum
from typing import Dict

import jsonpickle
from jsonpickle.handlers import BaseHandler


class EnumHandler(BaseHandler):
    def restore(self, obj):
        raise NotImplementedError

    def flatten(self, value: Enum, data: Dict):
        return value.name

jsonpickle.register(Enum, handler=EnumHandler, base=True)
