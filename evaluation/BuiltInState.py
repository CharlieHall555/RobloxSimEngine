from __future__ import annotations

import typing

if typing.TYPE_CHECKING:
    from classes.meta_classes.state import State

from classes.lua_classes.table import table
from classes.lua_classes.vector3 import Vector3Library
from classes.roblox_classes.instance import InstanceLibrary

from classes.lua_classes.table import set_metatable , get_metatable , rawget , rawset

from evaluation.DataModelGenerator import generate_data_model

from functions.built_in_functions import built_in_print

def setup_state(state : State) -> None:
    state.built_in_memory["game"] = state.datamodel
    state.built_in_memory["print"] = built_in_print
    state.built_in_memory["table"] = table
    state.built_in_memory["Vector3"] = Vector3Library
    state.built_in_memory["Instance"] = InstanceLibrary
    state.built_in_memory["setmetatable"] = set_metatable
    state.built_in_memory["getmetatable"] = get_metatable
    state.built_in_memory["rawget"] = rawget
    state.built_in_memory["rawset"] = rawset
