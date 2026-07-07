from __future__ import annotations
 
from typing import List, Any , Dict, TYPE_CHECKING, Tuple

from evaluation import function_call_wrapper

if TYPE_CHECKING:
    from classes.meta_classes.state import State
    from post_evaluation.Objective import Objective, FunctionCall

def eval_expected_function_calls(state: State,expected_function_calls: List[FunctionCall]) -> Tuple[bool, str]:
    for fc in expected_function_calls:
        result = function_call_wrapper(state, fc.function_name , fc.function_args)
        if result is None:
            return False, f"Function {fc.function_name} was not called."
        if result != fc.function_expected_output:
            return False, (
                f"{fc.function_name}{fc.function_args} returned {result}, "
                f"expected {fc.function_expected_output}."
            )
    return True, ""
    
def eval_expected_output(output : List[str], expected_output: List[Any]) -> Tuple[bool, str]:
    idx = 0
    for tag in output:
        if idx < len(expected_output) and tag == expected_output[idx]:
            idx += 1
            if idx == len(expected_output):
                break
    if idx != len(expected_output):
        missing = expected_output[idx:]
        return False, f"Expected tags missing or out of order: {missing}."
    return True, ""

def eval_expected_memory(memory : List[Dict[str , Any]],expected_memory: Dict[str, Any]) -> Tuple[bool, str]:
    global_mem = memory[0]
    for var_name, expected_value in expected_memory.items():
        actual_value = global_mem.get(var_name, None)
        if actual_value != expected_value:
            return False, f"Var value mismatch: '{var_name}' is {actual_value}, expected {expected_value}."
    return True, ""



