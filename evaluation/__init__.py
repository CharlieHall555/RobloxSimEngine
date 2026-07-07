from typing import Tuple , Union , Any , List

from evaluation.EvaluationEngine import eval_function_call, eval_identifier
from syntax_tree.ASTNodes import FunctionCallNode, VarNode, ArgsNode

def function_call_wrapper(state , function_name:str="" , args : List[Any] = []) -> Union[Tuple[Any] , None]:
    
    function_call = FunctionCallNode(VarNode(function_name) , ArgsNode(args))
    
    return eval_function_call(state , function_call)
