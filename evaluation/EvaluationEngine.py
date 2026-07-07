from __future__ import annotations
import time
import typing
import classes

import syntax_tree.ASTNodes as AST

from evaluation.ErrorDisplay import *

from evaluation.Util import *
from evaluation.ExpressionEvaluation import *
from classes.meta_classes.state import State
from classes.lua_classes.indexable import Indexable

def eval_protect(state : State) -> None:
    if (time.perf_counter() - state.start_time) > state.max_run_time:    
        raise TimeoutError

def eval_block(state : State  , block : AST.BlockNode , keep_state : bool = False):
    eval_protect(state)

    if isinstance(block , AST.BlockNode):
        returns = eval_sequence(state , block.sequence)
        if keep_state == False: state.memory.pop()
        return returns
    else:
        raise RuntimeError(f"Expected block node got: {type(block)}")

def eval_sequence(state : State, seq : AST.SequenceNode) -> bool:
    eval_protect(state)
    returns : bool
    if isinstance(seq , AST.SequenceNode):
        statements : typing.List[AST.ASTNode] = seq.statements
        for each in statements:
            stat_returns = eval_statement(state , each)
            if stat_returns:
                return True
        return False
    else:   
        raise RuntimeError(f"Expected SequenceNode got: {type(seq)}")


def eval_multi_assignment(state : State, assg : AST.MultiAssignmentNode):
    eval_protect(state)
    var_list : typing.List[AST.IdentifierBase]
    exp_list : typing.List[AST.ExpressionBase]

    var_list = assg.targets
    exp_list = assg.values

    i = 0
    exp_i = 0

    while i < len(var_list):
        var_name : str 
        each_id : AST.IdentifierBase = var_list[i]

        if isinstance(each_id , AST.VarNode):
            var_name = each_id.value
        elif isinstance(each_id , AST.AttributeName):
            raise NotImplementedError()
        else:
            break


        if i > len(exp_list):
            set_variable(state , var_name , nil)
            i += 1
            exp_i += 1
            continue

        exp : AST.ExpressionBase = exp_list[exp_i]
        evaluated_exp : typing.Any
       
        if isinstance(exp , AST.FunctionCallNode):
            evaluated_exp = eval_function_call(state , exp)
            
            if evaluated_exp is None:
                continue

            list_exp = list(evaluated_exp)
            n_exp = len(list_exp)

            for j in range(0 , n_exp):
                current = i + j
                each_id = var_list[current]
                if isinstance(each_id , AST.VarNode):
                    var_name = each_id.value
                elif isinstance(each_id , AST.AttributeName):
                    raise NotImplementedError()
                else:
                    break

                set_variable(state , var_name , list_exp[j])
            i += n_exp
        else:
            evaluated_exp = eval_expression(state , exp)
            set_variable(state , var_name , evaluated_exp)
            i += 1
        exp_i += 1

def set_attribute(state : State , base : typing.Union[AST.VarNode , AST.AttributeNode] , attr : AST.AttributeNode , new_value : typing.Any):

    base_object : typing.Any

    base_object = eval_identifier(state , base)

    if isinstance(base_object , Indexable):

        if attr.property is AST.AttributeNode:
            raise NotImplemented
        elif isinstance(attr.property , AST.ExpressionBase):
            attr_name : typing.Any = eval_expression(state , attr.property)
            base_object.set_value(attr_name , new_value)
        else:
            raise RuntimeError
            

    else:
        raise RuntimeError


def eval_assignment(state : State , assg : AST.AssignmentNode):
    eval_protect(state)
    id : AST.VarNode = assg.target

    value : typing.Union[bool , float, str , NilClass] = 0

    if isinstance(assg.value , AST.VarNode):
        value = eval_identifier(state , assg.value)
    elif isinstance(assg.value , AST.FunctionCallNode):
        value = eval_function_call(state , assg.value)
    elif isinstance(assg.value , AST.TableConstructor):
        value = eval_table_constructor(state , assg.value)
    elif isinstance(assg.value , AST.ExpressionBase):
        value = eval_expression(state , assg.value)
    elif isinstance(assg.value , AST.FunctionDefinitionNode):
        value = assg.value
    else:
        raise RuntimeError

    if isinstance(assg.target , AST.VarNode):
        set_variable(state , id.value , value , local=assg.local)
    elif isinstance(assg.target , AST.AttributeNode):
        set_attribute(state , assg.target.base , assg.target , value)
    else:
        raise RuntimeError  

# ----------- STRUCTURE EVALUATION -----------

def eval_if(state : State , if_stat : AST.IfNode) -> bool:
    eval_protect(state)
    returns : bool
    condition = eval_expression(state , if_stat.condition)
    
    if condition == False: #or nil
        if if_stat.else_block is not None and isinstance(if_stat.else_block , AST.BlockNode):
            state.memory.append({})
            returns = eval_block(state , if_stat.else_block)
        elif if_stat.else_block is not None:
            returns = eval_if(state , if_stat.else_block)
    else:
        state.memory.append({})
        returns = eval_block(state , if_stat.then_block)

    return returns
        
def eval_for(state : State , for_loop : AST.ForNode) -> bool:
    eval_protect(state)
    returns : bool  = False
    iterator : AST.VarNode = for_loop.iterator
    start : typing.Any = eval_expression(state , for_loop.start)
    end : typing.Any = eval_expression(state , for_loop.end)
    step : typing.Any = eval_expression(state , for_loop.step)

    i = start

    if step > 0:
        while i <= end and returns == False:
            state.memory.append({iterator.value: i})
            returns = eval_block(state , for_loop.block)
            i += step
    else:
        while i >= end and returns == False:
            state.memory.append({iterator.value: i})
            returns = eval_block(state , for_loop.block)
            i += step

    return returns

def eval_while(state : State , while_node : AST.WhileNode) -> bool:
    eval_protect(state)
    returns : bool = False
    condition : typing.Any = eval_expression(state , while_node.condition)
    while condition == True and returns == False:
        state.memory.append({})
        returns = eval_block(state , while_node.block)
        condition = eval_expression(state , while_node.condition)
    return returns

def eval_repeat(state : State , repeat_node : AST.RepeatNode) -> bool:
    eval_protect(state)
    condition : typing.Any = False
    returns : bool = False
    while condition == False and returns == False:
        state.memory.append({})
        returns = eval_block(state , repeat_node.block)
        condition = eval_expression(state , repeat_node.condition)
    return returns

# ---------------------------------

def eval_statement(state : State, statement : AST.ASTNode):
    eval_protect(state)
    if isinstance(statement , AST.AssignmentNode):
        eval_assignment(state , statement)
        return False
    elif isinstance(statement , AST.MultiAssignmentNode):
        eval_multi_assignment(state , statement)
        return False
    elif isinstance(statement , AST.SequenceNode):
        return eval_sequence(state , statement)
    elif isinstance(statement , AST.ForNode):
        return eval_for(state , statement)
    elif isinstance(statement , AST.IfNode):
        return eval_if(state , statement)
    elif isinstance(statement , AST.WhileNode):
        return eval_while(state , statement)
    elif isinstance(statement , AST.RepeatNode):
        return eval_repeat(state , statement)
    elif isinstance(statement , AST.FunctionDefinitionNode):
        eval_function_def(state , statement)
        return False
    elif isinstance(statement , AST.ReturnStatmentBase):
        return eval_return(state , statement)
    elif isinstance(statement , AST.FunctionCallNode):
        eval_function_call(state , statement)
        return False
    elif isinstance(statement , AST.BlockNode):
        return eval_block(state , statement)
    else:
        raise RuntimeError(f"{statement}")

def eval_return(state : State , statement : AST.ReturnNode) -> bool:
    eval_protect(state)
    result = eval_expression_list(state , statement.ExpressionList)
    state.return_result.append(result)
    return True

def eval_function_def(state : State , function_def : AST.FunctionDefinitionNode):
    eval_protect(state)
    set_variable(state , function_def.name.value , function_def, local=False)

def eval(state : State, ast : AST.BlockNode):
    eval_protect(state)
    eval_block(state , ast , keep_state=True)
    return state