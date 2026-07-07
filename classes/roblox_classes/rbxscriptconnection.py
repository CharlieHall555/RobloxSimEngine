from __future__ import annotations

from classes.lua_classes import LuaTable
from evaluation.EvaluationEngine import eval_identifier
from syntax_tree.ASTNodes import IdentifierBase, FunctionDefinitionNode

import typing

if typing.TYPE_CHECKING:
    from classes.meta_classes.state import State


class RBXScriptConnection(LuaTable):
    event_name : str
    target_function : FunctionDefinitionNode
    def __init__(self , event_name : str , target_function : FunctionDefinitionNode):
        self.event_name = event_name
        self.target_function = target_function
        super().__init__({})
        
    def __repr__(self):
        return str(self)
    
    def __str__(self):
        return "<" + self.event_name + ">"