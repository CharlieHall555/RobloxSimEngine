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

def build_anon_function(main : ASTBuilder , ctx : LuaParser.FunctiondefContext) -> AST.FunctionDefinitionNode:

    params : typing.List[AST.VarNode]
    function_body : AST.BlockNode

    params , function_body = main.safeVisit(ctx.funcbody())

    return AST.FunctionDefinitionNode(None , function_body , params)