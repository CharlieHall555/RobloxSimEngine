from classes.roblox_classes.instance import Instance
from classes.meta_classes.state import State
from classes.lua_classes.nil import nil

def get_service(state : State , self : "Datamodel" , service_name : str):
    return (self.get_value(service_name))

class Datamodel(Instance): #in roblox known as "game" or "Game"
    def __init__(self):
        super().__init__()

    