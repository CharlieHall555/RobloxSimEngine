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

def build_while(main , ctx : LuaParser.StatContext) -> AST.WhileNode:
    c = ctx.getChildCount()

    condition : AST.ExpressionBase = main.safeVisit(ctx.getChild(1))
    block : AST.BlockNode = main.safeVisit(ctx.getChild(3))
    return AST.WhileNode(condition , block)