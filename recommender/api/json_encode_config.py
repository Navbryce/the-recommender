from enum import Enum
from typing import Dict

import jsonpickle
from jsonpickle.handlers import BaseHandler


class CamelCaseHandler(BaseHandler):
    def restore(self, obj):
        raise NotImplementedError

    def flatten(self, value: any, data: Dict):
        return value


class EnumHandler(BaseHandler):
    def restore(self, obj):
        raise NotImplementedError

    def flatten(self, value: Enum, data: Dict):
        return value.name


jsonpickle.register(object, CamelCaseHandler)
jsonpickle.register(Enum, handler=EnumHandler, base=True)
