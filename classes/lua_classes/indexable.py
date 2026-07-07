import typing
from classes.lua_classes.nil import NilClass , nil

class Indexable:
    values : typing.Dict[str , typing.Any]
    
    def __init__(self):
        self.values = {}
    
    def set_value(self , value_name , value):
        self.values[value_name] = value

    def has_key(self, key: str) -> bool:
        return key in self.values

    def get_value(self , value_name) -> typing.Union[typing.Any , NilClass]:
        return self.values.get(value_name , nil)

    def __getitem__(self, key):
        return self.values.get(key, None)

    def __setitem__(self, key, value):
        self.values[key] = value