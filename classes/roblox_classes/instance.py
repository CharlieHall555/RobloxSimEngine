from __future__ import annotations

from typing import Any, Optional, List
from classes.lua_classes import Indexable
from classes.lua_classes import LuaTable
from classes.lua_classes import NilClass, nil
from classes.meta_classes.childlist import ChildrenList

import uuid

def create_instance(_ , instance_name : str):
    from classes.roblox_classes import class_mappings
    constructor = class_mappings.get(instance_name , Instance)
    return constructor()

def get_children(_ , instance : "Instance") -> List["Instance"]:
    return instance.children.all()

class Instance(Indexable):
    id: int
    parent: Optional["Instance"]
  
    def __init__(self):
        super().__init__()
        self.id = int(uuid.uuid4())
        self.parent = None
        self.name = "Instance"
        self.set_value("Name" , self.name)
        self.set_value("GetChildren" , get_children)
        self.children = ChildrenList()
        
    def get_value(self, value_name) -> Any | NilClass:
        if self.children.contains(value_name):
            return self.children.get_child(value_name)
        elif value_name == "Name":
            return self.name
        else:
            return super().get_value(value_name)

    def set_value(self , value_name , value):
        if value_name == "Parent":
            self.set_parent(value)
        elif value_name == "Name":
            self.name = value
            if self.parent:
                self.parent.children.on_name_change(self , self.name)
        super().set_value(value_name , value)

    def remove_child(self , to_remove : "Instance"):
        if not isinstance(to_remove, Instance):
            raise TypeError(f"to_remove must be an instance of Instance or its subclass, got {type(to_remove)}")
        
        self.children.remove_child(to_remove)

    def add_child(self, new_child: "Instance"):
        if not isinstance(new_child, Instance):
            raise TypeError(f"new_child must be an instance of Instance or its subclass, got {type(new_child)}")

        self.children.add_child(new_child)

    def set_parent(self , new_parent: "Instance"):
        if not isinstance(new_parent , Instance):
            raise TypeError(f"newparent must be an instance of Instance or its subclass, got {type(new_parent)}")
        
        if self.parent:
            self.parent.remove_child(self)
        self.values["Parent"] = new_parent
        self.parent = new_parent
        new_parent.add_child(self)



InstanceLibrary = LuaTable(
    {"new" : create_instance}
)