from typing import Dict


class PersistenceObject:
    def __get_public_attributes__(self) -> Dict:
        return {key: value for key, value in self.__dict__.items() if key[0] != "_"}

    def __repr__(self):
        return f'{self.__class__.__name__} {{{ ", ".join([f"{key}={value}" for key, value in  self.__dict__.items()])}}}'
