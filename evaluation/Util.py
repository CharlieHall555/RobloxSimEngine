from __future__ import annotations

import typing

import syntax_tree.ASTNodes as AST
from classes.lua_classes.nil import nil

if typing.TYPE_CHECKING:
    from classes.meta_classes.state import State

# ------------------- UTILITIES -------------------

def copy_state(g_state):
    return g_state.copy()

def lookup(state : State , name : str) -> typing.Any:
    
    for local_state in reversed(state.memory):
        if name in local_state.keys():
            return local_state.get(name , nil)

    if name in state.built_in_memory.keys():
        return state.built_in_memory.get(name , nil)
    else:
        return nil
    
def set_variable(state : State , name : str , value : typing.Any , local=False) -> None:
    if local:
        state.memory[-1][name] = value
        return

    for local_state in reversed(state.memory):
        if name in local_state:
            local_state[name] = value
            return

    if name in state.built_in_memory.keys():
        state.built_in_memory[name] = value
    else:
        state.memory[0][name] = value
   
def is_indexable(obj : typing.Any) -> bool:
    if hasattr(obj , "indexable"):
        if obj.indexable == True:
            return True
    return False

def get_current_function_name(state : State) -> typing.Optional[str]:
    if len(state.current_function) <= 0:
        return None
    else:
        return state.current_function[-1]

# ---------------------------------------------------------