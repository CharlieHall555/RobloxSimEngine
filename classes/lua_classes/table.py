from classes.lua_classes.indexable import Indexable
import typing
from classes.lua_classes.nil import nil,  NilClass

def insert(_, table : "LuaTable" , *args):

    if len(args) == 1:
        value = args[0]
        table.values[str(len(table.values)+1)] =  value
    elif len(args) == 2:
        value = args[1]
        position = str(args[0])

        if position < 1 or position > len(table.values):
            raise RuntimeError

        result = {}
        for k, v in table.values.items():
            if isinstance(k, int) and k >= position:
                result[k + 1] = v
            else:
                result[k] = v 
        table.values = result
        table.values[position] =  value
    else:
        raise RuntimeError
    
def get_metatable(_,table : "LuaTable") -> typing.Union["LuaTable" , NilClass ]:
    if table.metatable is None:
        return nil
    return table.metatable
    
def set_metatable(_,table : "LuaTable", mt: "LuaTable") -> None:
    if isinstance(table , LuaTable):
        table.metatable = mt   
    else:
        raise RuntimeError
  

def rawget(_,table : "LuaTable", key: str):
    return table.values.get(key, nil)

def rawset(_,table : "LuaTable", key: str, value: typing.Any):
    table.values[key] = value

class LuaTable(Indexable):
    metatable : typing.Optional["LuaTable"]
    def __init__(self , values={}):
        super().__init__()
        self.metatable = None
        self.values = values

    def get_value(self, key: str) -> typing.Any:
        if key in self.values.keys():
            return self.values[key]

        if self.metatable is not None:
            idx = rawget(None , self.metatable , "__index")
            if isinstance(idx, LuaTable):
                return idx.get_value(key)
            elif callable(idx):
                return idx(self, key)
        return nil

    def set_value(self, key: str, value: typing.Any):
        if key in self.values.keys():
            self.values[key] = value
            return

        if self.metatable is not None:
            newidx = rawget(None , self.metatable , "__index")
            if isinstance(newidx, LuaTable):
                newidx.set_value(key, value)
                return
            elif callable(newidx):
                newidx(self, key, value)
                return

        self.values[key] = value

    def __repr__(self):
        return f"<LuaTable {self.values!r}>"

    def __str__(self):
        if self.metatable and self.metatable is LuaTable:
            tostr = rawget(None , self.metatable, "__tostring")
            if callable(tostr):
                return tostr(self)
        return f"{self.values!r}"
    
table = LuaTable({"insert" : insert})
