from typing import Dict


class Serializable:
    @staticmethod
    def to_camel_case(value: str) -> str:
        pascal = "".join([value.title() for value in value.split("_")])
        return pascal[0].lower() + pascal[1:]

    def __getstate__(self) -> Dict:
        return {
            Serializable.to_camel_case(key): value
            for key, value in self.__dict__.items()
        }
