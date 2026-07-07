from __future__ import annotations

from parser.LuaParserVisitor import LuaParserVisitor
from parser.LuaParser import LuaParser
import syntax_tree.ASTNodes as AST
from syntax_tree.ASTNodes import ASTNode
import parser.LuaLexer as LuaLexer
import typing

def build_repeat(main , ctx : LuaParser.StatContext) -> AST.RepeatNode:        
    block : AST.BlockNode = main.safeVisit(ctx.getChild(1))
    expression : AST.ExpressionBase = main.safeVisit(ctx.getChild(3))

    return AST.RepeatNode(block , expression)

