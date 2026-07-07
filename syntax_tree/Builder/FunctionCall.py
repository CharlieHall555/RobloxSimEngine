from __future__ import annotations

from parser.LuaParserVisitor import LuaParserVisitor
from parser.LuaParser import LuaParser
import syntax_tree.ASTNodes as AST
from syntax_tree.ASTNodes import ASTNode
import parser.LuaLexer as LuaLexer
import typing
from syntax_tree.Builder.Misc import build_bracket_or_dot

if typing.TYPE_CHECKING:
    from syntax_tree.ASTBuilder import ASTBuilder
 
def __init__():
    pass

def build_simple_call(main : ASTBuilder , ctx : LuaParser.FunctioncallContext , args : AST.ArgsNode) -> AST.FunctionCallNode:
    func_name = AST.VarNode(ctx.getChild(0).getText())
    function_call = AST.FunctionCallNode(func_name , args)
    return function_call

def build_expression_call(main : ASTBuilder , ctx : LuaParser.FunctioncallContext , args : AST.ArgsNode) -> AST.FunctionCallNode | AST.IdentifierBase:
    base_exp : AST.ExpressionBase
    base_exp = main.safeVisit(ctx.getChild(1))

    if ctx.getChildCount() == 3:
        if isinstance(base_exp , AST.IdentifierBase):
            function_call = AST.FunctionCallNode(base_exp , args)
            return function_call
        else:
            raise RuntimeError
    elif ctx.getChild(3).getText() in ["." , "["]:
        if isinstance(base_exp , AST.IdentifierBase) or isinstance(base_exp , AST.FunctionCallNode):
            return build_bracket_or_dot(
                main,
                ctx,
                base_exp,
                3,
                ctx.getChildCount() - 1
            )
        else:
            raise SyntaxError
    else:
        raise SyntaxError

def build_method_call(main: ASTBuilder, ctx: LuaParser.FunctioncallContext, args: AST.ArgsNode) -> AST.FunctionCallNode:
    
    colon_index = None
    for i in range(ctx.getChildCount()):
        if ctx.getChild(i).getText() == ":":
            colon_index = i
            break

    if colon_index is None:
        raise SyntaxError("Colon not found in method call")

    base_expr_ctx = ctx.getChild(0)
    base_expr : AST.IdentifierBase

    if ctx.NAME():
        base_expr = AST.VarNode(base_expr_ctx.getText())
    elif ctx.functioncall(): 
        base_expr = main.safeVisit(ctx.functioncall())
    elif ctx.getChild(0).getText() == "(": 
        base_expr = main.safeVisit(ctx.getChild(1))
    else:
        raise SyntaxError("Unexpected base in method call")

    if colon_index > 1:
        base_expr = build_bracket_or_dot(main, ctx, base_expr, 1, colon_index - 1)

    method_name = ctx.getChild(colon_index + 1).getText()
    method_attr = AST.AttributeNode(base=base_expr, property=AST.StringNode(method_name))

    return AST.MethodCallNode(base_expr , method_attr, args)

def build_recursive_call(main: ASTBuilder, ctx: LuaParser.FunctioncallContext, args: AST.ArgsNode) -> AST.FunctionCallNode:
    base_call = main.safeVisit(ctx.functioncall())

    if ctx.getChildCount() > 2:
        chained = build_bracket_or_dot(
            main,
            ctx,
            base_call,
            1,
            ctx.getChildCount() - 2 
        )
        return AST.FunctionCallNode(chained, args)

    return AST.FunctionCallNode(base_call, args)

def build_function_call(main : ASTBuilder , ctx : LuaParser.FunctioncallContext) -> AST.FunctionCallNode | AST.IdentifierBase:
    args : AST.ArgsNode

    if ctx.args():
        args = main.safeVisit(ctx.args())


    if ctx.COL():
        return build_method_call(main, ctx, args)
    if ctx.NAME() and ctx.getChildCount() == 2:
        return build_simple_call(main , ctx , args)
    elif ctx.NAME() and (not ctx.COL() and not ctx.functioncall() and ctx.getChild(0).getText() != "("): 
        func_name = build_bracket_or_dot(main , ctx , AST.VarNode(ctx.getChild(0).getText()) , 1 , ctx.getChildCount() - 1)
        return AST.FunctionCallNode(func_name , args)
    elif ctx.getChild(0).getText() == "(":
        return build_expression_call(main , ctx , args)
    elif ctx.functioncall():
        return build_recursive_call(main , ctx , args)

    else:
        raise SyntaxError("NoPattern")