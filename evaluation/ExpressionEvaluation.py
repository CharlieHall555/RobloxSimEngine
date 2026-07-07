# ------------------- EXPRESSION EVALUATIONS -------------------
from __future__ import annotations

import typing
from classes.lua_classes.nil import nil, NilClass
from classes.lua_classes.table import LuaTable
from classes.lua_classes.lua_number import LuaNumber
from classes.lua_classes.indexable import Indexable
from evaluation.Util import *

import syntax_tree.ASTNodes as AST

from evaluation.ErrorDisplay import *

def eval_expression_list(state , exp_list : typing.List[AST.ExpressionBase]):
    output = []
    each_exp : AST.ExpressionBase
    for each_exp in exp_list:
        output.append(eval_expression(state , each_exp))
    return tuple(output)

def eval_property(state : State , attr_name : AST.AttributeName | AST.ExpressionBase) -> typing.Any:
    if isinstance(attr_name , AST.AttributeName):
        return eval_expression(state , attr_name.value)
    elif isinstance(attr_name , AST.ExpressionBase):
        return eval_expression(state , attr_name)
    raise RuntimeError  

def eval_attribute(state : State , attr : AST.AttributeNode) -> typing.Any:

    print("attr=",attr)

    base : typing.Any = None
    accessed = eval_property(state , attr.property)
    print("acc=" , accessed)
    if isinstance(attr.base , AST.IdentifierBase):
        base = eval_identifier(state , attr.base)
        print(base)

    if base and isinstance(base , Indexable):
        return base.get_value(accessed)
    else:
        raise RuntimeError(f"{attr.base} of {type(base)} is not indexable")

def eval_identifier(state : State, id : AST.IdentifierBase) -> typing.Any:
    if isinstance(id , AST.VarNode):
        return lookup(state , id.value)
    elif isinstance(id , AST.AttributeNode):
        return eval_attribute(state , id)
    else:
        raise RuntimeError


def eval_expression(state , exp : AST.ExpressionBase) -> typing.Union[LuaNumber , bool , str , NilClass, LuaTable]:
    if isinstance(exp , AST.ExpressionBase):
        if isinstance(exp , AST.StringNode) or isinstance(exp , AST.BoolNode):
            return exp.value
        if isinstance(exp , AST.NumberNode):
            return LuaNumber(exp.value)
        elif isinstance(exp , AST.IdentifierBase):
            return eval_identifier(state , exp)
        elif isinstance(exp , AST.FunctionCallNode):
            return eval_function_call(state , exp)
        elif isinstance(exp , AST.FunctionDefinitionNode):
            return exp
        elif isinstance(exp , AST.TableConstructor):
            return eval_table_constructor(state , exp)
        elif isinstance(exp , AST.UnaryNode):
            if exp.op.value == "-":
                return eval_negation(state , exp)
            elif exp.op.value == "not":
                return eval_not(state , exp)
            else:
                raise RuntimeError(f"unexpected unary operation {exp.op.value}")
        elif isinstance(exp , AST.ExpressionNode):
            #define operation
            if exp.op.value == "+":
                return eval_add(state , exp)
            elif exp.op.value == "*":
                return eval_mul(state , exp)
            elif exp.op.value == "==":
                return eval_equality(state , exp)
            elif exp.op.value == "~=":
                return eval_non_equality(state , exp)
            elif exp.op.value == "-":
                return eval_minus(state , exp)
            elif exp.op.value == "/":
                return eval_div(state , exp)
            elif exp.op.value == "%":
                return eval_mod(state , exp)
            elif exp.op.value == "//":
                return eval_int_div(state , exp)
            elif exp.op.value == "and":
                return eval_and(state , exp)
            elif exp.op.value == "or":
                return eval_or(state , exp)
            elif exp.op.value == ">":
                return eval_greater(state , exp)
            elif exp.op.value == "<":
                return eval_less(state , exp)
            elif exp.op.value == ">=":
                return eval_greater_eq(state , exp)
            elif exp.op.value == "<=":
                return eval_less_eq(state , exp)
            elif exp.op.value == "..":
                return eval_concat(state , exp)
            else:
                raise RuntimeError(f"unexpected operation {exp.op.value}")
        else:
            raise RuntimeError
    else:
        raise RuntimeError(f"expected ExpressionBase, got {type(exp)}")

# ------------------- TABLE CONSTRUCTOR -------------------

def eval_table_constructor(state : State , constructor : AST.TableConstructor) -> LuaTable:

    new_table = LuaTable({})

    fields = constructor.fields
    if len(fields) <= 0:
        return new_table
    else:
        each_field : AST.FieldNode
        for i , each_field in enumerate(constructor.fields):
            
            field_name =  eval_expression(state , each_field.field_name) if each_field.field_name else int(i + 1)
            field_value = eval_expression(state , each_field.field_value)

            if field_name is LuaNumber:
                field_name = round(int(field_name))

            if isinstance(field_name , int) or isinstance(field_name , str):
                new_table.set_value(field_name , field_value)
            else:
                raise RuntimeError  
        
        return new_table


# ------------------- COMPARISON EVALUATIONS -------------------

def eval_equality(state , exp : AST.ExpressionNode) -> bool:

    try:
        val1 = eval_expression(state , exp.exp1)
        val2 = eval_expression(state , exp.exp2)
        return val1 == val2 #type: ignore
    except:
        raise RuntimeError
    
def eval_non_equality(state , exp : AST.ExpressionNode) -> bool:
    

    try:
        val1 = eval_expression(state , exp.exp1)
        val2 = eval_expression(state , exp.exp2)
        return val1  != val2
    except:
        raise RuntimeError

def eval_greater(state , exp : AST.ExpressionNode) -> bool:

    try:
        val1 = eval_expression(state , exp.exp1)
        val2 = eval_expression(state , exp.exp2)
        return val1  > val2 #type: ignore
    except:
        raise RuntimeError

def eval_concat(state , exp : AST.ExpressionNode) -> str:
    
    try:
        val1 = eval_expression(state , exp.exp1)
        val2 = eval_expression(state , exp.exp2)
        val1 = str(val1)
        val2 = str(val2)
        return val1 + val2
    except:
        raise RuntimeError
  


def eval_less(state , exp : AST.ExpressionNode) -> bool:

    try:
        val1 = eval_expression(state , exp.exp1)
        val2 = eval_expression(state , exp.exp2)
        return val1 < val2 #type: ignore
    except:
        raise RuntimeError
    
def eval_greater_eq(state , exp : AST.ExpressionNode) -> bool:

    try:
        val1 = eval_expression(state , exp.exp1)
        val2 = eval_expression(state , exp.exp2)
        return val1 >= val2 #type: ignore
    except:
        raise RuntimeError

def eval_less_eq(state , exp : AST.ExpressionNode) -> bool:

    try:
        val1 = eval_expression(state , exp.exp1)
        val2 = eval_expression(state , exp.exp2)
        return val1 <= val2 #type: ignore
    except:
        raise RuntimeError

# ------------------- NUMERIC EVALUATIONS -------------------
 
def eval_minus(state, exp : AST.ExpressionNode) -> LuaNumber:
      
    try:
        val1 = eval_expression(state , exp.exp1)
        val2 = eval_expression(state , exp.exp2)
        return val1 - val2 #type: ignore
    except:
        raise RuntimeError

def eval_add(state , exp : AST.ExpressionNode) -> LuaNumber:
    
    val1 = nil
    val2 = nil

    try:
        val1 = eval_expression(state , exp.exp1)
        val2 = eval_expression(state , exp.exp2)
        return val1 + val2 #type: ignore
    except:
        raise_add_type_error(state , val1, val2) 
        return LuaNumber(0)
    
def eval_mul(state , exp : AST.ExpressionNode) -> LuaNumber:
    
    val1 = nil
    val2 = nil

    try:
        val1 = eval_expression(state , exp.exp1)
        val2 = eval_expression(state , exp.exp2)
        return val1 * val2 #type: ignore
    except:
        raise_mul_type_error(state , val1 , val2)
        return LuaNumber(0)

def eval_div(state, exp : AST.ExpressionNode) -> LuaNumber:
    
    try:
        val1 = eval_expression(state , exp.exp1)
        val2 = eval_expression(state , exp.exp2)
        return val1 / val2 #type: ignore
    except:
        raise RuntimeError
    
def eval_mod(state, exp : AST.ExpressionNode) -> LuaNumber:
    
    try:
        val1 = eval_expression(state , exp.exp1)
        val2 = eval_expression(state , exp.exp2)
        return val1 % val2 #type: ignore
    except:
        raise RuntimeError
    
def eval_int_div(state, exp : AST.ExpressionNode) -> LuaNumber:
    
    try:
        val1 = eval_expression(state , exp.exp1)
        val2 = eval_expression(state , exp.exp2)
        return val1 // val2 #type: ignore
    except:
        raise RuntimeError
    
# ------------------- LOGIC EVALUATIONS -------------------
    
def eval_and(state , exp : AST.ExpressionNode) -> bool:
    
    try:
        val1 = eval_expression(state , exp.exp1)
        val2 = eval_expression(state , exp.exp2)
        return val1 and val2 #type: ignore
    except:
        raise RuntimeError
    
def eval_or(state , exp : AST.ExpressionNode) -> typing.Any:
    try:
        val1 = eval_expression(state , exp.exp1)
        val2 = eval_expression(state , exp.exp2)
        return val1 or val2 #type: ignore
    except:
        raise RuntimeError
    
# ------------------- UNARY EVALUATIONS -------------------  

def eval_not(state , exp : AST.UnaryNode) -> bool:
    val1 = eval_expression(state , exp.exp)
    try:
        if isinstance(val1 , bool):
            return not val1 
        else:
            raise RuntimeError
    except:
        raise RuntimeError

def eval_negation(state , exp : AST.UnaryNode) -> LuaNumber:
    val1 = eval_expression(state , exp.exp)
    try:
        if isinstance(val1 , LuaNumber):
            return -(val1) #type: ignore
        else:
            raise RuntimeError
    except:
        raise RuntimeError

# ------------------- FUNCTION CALL -------------------  

def eval_function_call(state : State , function_call : AST.FunctionCallNode) -> typing.Union[typing.Tuple , None]:
    from evaluation.EvaluationEngine import eval_statement

    function_def : typing.Union[AST.FunctionDefinitionNode , typing.Callable]
    function_name : str
    return_result : typing.Any
    args : AST.ArgsNode

    if isinstance(function_call.func_name, AST.VarNode):
        function_def = lookup(state , function_call.func_name.value)
        function_name = function_call.func_name.value
        args = function_call.args

    elif isinstance(function_call , AST.MethodCallNode):

        function_def = eval_attribute(state , function_call.func_name)
        function_name = eval_expression(state , function_call.func_name.property) #type: ignore

        base = eval_identifier(state , function_call.func_name.base)

        args = function_call.args

        args = AST.ArgsNode([base] + args.args)

    elif isinstance(function_call.func_name , AST.AttributeNode):
       
        if isinstance(function_call.func_name.base , AST.AttributeName) or isinstance(function_call.func_name.base , AST.VarNode):
            
            function_name = eval_expression(state , function_call.func_name.property)
            function_def = eval_attribute(state , function_call.func_name)
            args = function_call.args

        elif isinstance(function_call.func_name.base , AST.FunctionCallNode):
            raise NotImplementedError
    else:
        raise RuntimeError

    print(function_def)

    if isinstance(function_def , AST.FunctionDefinitionNode):

        function_state : dict = {}

        for i in range(len(function_def.params)):
            key = function_def.params[i].value
            function_state[key] = eval_expression(state , args.args[i]) if i < len(args.args) else nil

        state.memory.append(function_state)
        state.current_function.append(function_name)

        return_result : typing.Union[typing.Tuple , None] = None

        for each_statement in function_def.body.sequence.statements:
            returns = eval_statement(state , each_statement)
            if returns:
                return_result = state.return_result.pop()
                if len(return_result) == 1:
                    return_result = return_result[0]
                break
                

        state.memory.pop()
        state.current_function.pop()
        return return_result
        
    elif callable(function_def):

        state.current_function.append(function_name)

        evaluated_args : typing.List[typing.Any] = []

        for each_arg in args.args:
            if isinstance(each_arg , AST.ExpressionBase):
                evaluated_args.append(eval_expression(state , each_arg))
            else:
                evaluated_args.append(each_arg)

        return_result = function_def(state , *evaluated_args)
        
        if return_result is tuple and len(return_result) == 1:
            return_result = return_result[0]
        state.current_function.pop()

        return return_result

    else:
        raise RuntimeError("function def isnt callable")
    
    return None
   
