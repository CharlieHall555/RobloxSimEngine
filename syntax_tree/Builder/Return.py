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

def build_return_statement(main : ASTBuilder , ctx : LuaParser.RetstatContext):
    if ctx.BREAK():
        return AST.BreakNode()
    elif ctx.CONTINUE():
        return AST.ContinueNode()
    elif ctx.RETURN() and ctx.explist():
        return AST.ReturnNode(main.safeVisit(ctx.explist()))
    elif ctx.RETURN():
        return AST.ReturnNode([])
    else:
        raise SyntaxError