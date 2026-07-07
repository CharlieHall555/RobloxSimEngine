from __future__ import annotations

from classes.lua_classes import LuaTable , set_metatable
from evaluation.EvaluationEngine import eval_identifier
from syntax_tree.ASTNodes import IdentifierBase, FunctionDefinitionNode
from classes.roblox_classes.rbxscriptconnection import RBXScriptConnection

import typing

if typing.TYPE_CHECKING:
    from classes.meta_classes.state import State

def connect_signal(state : State , signal : "RBXScriptSignal" , target_function):
    new_connection : RBXScriptConnection
    if isinstance(target_function , FunctionDefinitionNode):
        new_connection = RBXScriptConnection(signal.signal_name , target_function)
        state.event_connections.append(new_connection)
        return (new_connection)
    else:
        raise RuntimeError



RBXScriptSignalLibary = LuaTable(
    {"Connect" : connect_signal}
)


RBXScriptSignalMetatable = LuaTable({"__index" : RBXScriptSignalLibary})

class RBXScriptSignal(LuaTable):
    signal_name : str
    def __init__(self , signal_name : str):
        self.signal_name = signal_name
        super().__init__({})
        
        set_metatable(None, self , RBXScriptSignalMetatable)
        
