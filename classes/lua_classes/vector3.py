from classes.lua_classes.table import LuaTable
from classes.lua_classes.lua_number import LuaNumber

def new_vector_3(_,x , y , z) -> "Vector3":
    return Vector3(x , y , z)

class Vector3(LuaTable):
    def __init__(self , x : LuaNumber , y : LuaNumber , z : LuaNumber):
        super().__init__({})
        self.set_value("X" , x)
        self.set_value("Y" , y)
        self.set_value("Z" , z)

    def __repr__(self):
        return f"<Vector3 {self.values!r}>"
    
    def __add__(self : "Vector3" , other : "Vector3"):
        return new_vector_3(None,
            self.get_value("X") + other.get_value("X"),
            self.get_value("Y") + other.get_value("Y"),
            self.get_value("Z") + other.get_value("Z")
        )

Vector3Library = LuaTable({
    "new" : new_vector_3
})