from classes.roblox_classes.instance import Instance
from classes.lua_classes import Vector3
from classes.roblox_classes.rbxscriptsignal import RBXScriptSignal
from classes.lua_classes import LuaNumber as number

class Part(Instance):
    def __init__(self):
        super().__init__()
        self.set_value("Name" , "Part")
        self.set_value("Touched" , RBXScriptSignal("Touched"))
        self.set_value("Position" , Vector3(number(0) , number(0) , number(0)))
        self.set_value("Transparency" , number(0)) 

    def __repr__(self):
        return str(self)

    def __str__(self):
        return "Part"
