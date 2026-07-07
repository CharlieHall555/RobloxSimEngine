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

def build_prefix_exp_base(main : ASTBuilder, ctx : LuaParser.PrefixexpContext) -> AST.IdentifierBase: #rework types for this.
    base : AST.IdentifierBase
    last : AST.IdentifierBase
    base_exp = main.safeVisit(ctx.getChild(1))
    last = base_exp

    return build_bracket_or_dot(
        main,
        ctx,
        last,
        3
    )

def build_prefix_dot(main, ctx : LuaParser.PrefixexpContext) -> AST.IdentifierBase:
    base : AST.VarNode
    last : typing.Union[AST.VarNode , AST.AttributeNode]

    base = AST.VarNode(ctx.getChild(0).getText())      
    last = base
    return build_bracket_or_dot(
        main,
        ctx,
        last,
        1
    )

def build_prefix_function_base(main : ASTBuilder, ctx : LuaParser.PrefixexpContext )-> AST.IdentifierBase | AST.FunctionCallNode :
    
    base_call : AST.FunctionCallNode
    base_call = main.safeVisit(ctx.functioncall())

    if ctx.getChildCount() == 1:
        return base_call

    if ctx.getChild(1).getText() == ".":
        return build_bracket_or_dot(
            main,
            ctx,
            base_call,
            1
        )  
    elif ctx.getChild(1).getText() == "[":
        return build_bracket_or_dot(
            main,
            ctx,
            base_call,
            1
        )  
    else:
        raise SyntaxError

 


def build_prefix_square_brackets(main : ASTBuilder, ctx : LuaParser.PrefixexpContext) -> AST.IdentifierBase:
    base : AST.VarNode
    last : typing.Union[AST.VarNode , AST.AttributeNode]

    base = AST.VarNode(ctx.getChild(0).getText())
    last = base
    return build_bracket_or_dot(
        main,
        ctx,
        last,
        1
    )


def build_prefix_expression(main : ASTBuilder , ctx : LuaParser.PrefixexpContext) -> AST.IdentifierBase | AST.FunctionCallNode:
    if ctx.NAME() and ctx.getChildCount() == 1:
        return AST.VarNode(ctx.getText())
    elif ctx.functioncall():
        return build_prefix_function_base(main , ctx)
    elif ctx.getChild(1).getText() == '[':
        return build_prefix_square_brackets(main , ctx)
    elif ctx.getChild(1).getText() == '.':
        return build_prefix_dot(main , ctx)
    elif ctx.getChild(0).getText() == '(':
        return build_prefix_exp_base(main , ctx)
    else:
        raise SyntaxError