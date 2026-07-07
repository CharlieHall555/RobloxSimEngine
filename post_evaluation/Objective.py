from typing import Any , List , Dict, Tuple

class FunctionCall:

    function_name : str
    function_args : List[Any]
    function_expected_output : Tuple[Any]

    def __init__(self, function_name: str, function_args: List[Any], function_expected_output: Tuple[Any]):
        self.function_name = function_name
        self.function_args = function_args
        self.function_expected_output = function_expected_output

class Objective:
    output_tags : List[str] 
    state_variables : Dict[str , Any]
    expected_function_calls : List[FunctionCall]
    def __init__(self , output_tags : List[str] = [] , state_variables : Dict[str , Any] = {} , expected_function_calls:List[FunctionCall]=[]):
        self.output_tags = output_tags
        self.state_variables = state_variables
        self.expected_function_calls = expected_function_calls