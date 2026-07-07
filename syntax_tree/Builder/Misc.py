from __future__ import annotations

from parser.LuaParserVisitor import LuaParserVisitor
from parser.LuaParser import LuaParser
import syntax_tree.ASTNodes as AST
from syntax_tree.ASTNodes import ASTNode
import parser.LuaLexer as LuaLexer
import typing

if typing.TYPE_CHECKING:
    from syntax_tree.ASTBuilder import ASTBuilder

build_bracket_or_dot_context_type = typing.Union[
    LuaParser.FunctioncallContext,
    LuaParser.PrefixexpContext
]


def build_bracket_or_dot(main: ASTBuilder, ctx: typing.Union[LuaParser.FunctioncallContext, LuaParser.PrefixexpContext], base_node: typing.Union[AST.IdentifierBase , AST.FunctionCallNode],  start_index: int , end_index : typing.Optional[int] = None) ->  AST.IdentifierBase:
    index: int
    last: typing.Union[AST.IdentifierBase , AST.FunctionCallNode]
    index = start_index
    end = end_index or ctx.getChildCount()
    last = base_node
    while index < end :
        if ctx.getChild(index).getText() == '[':
            last = AST.AttributeNode(last, main.safeVisit(ctx.getChild(index+1)))
            index += 3
        elif ctx.getChild(index).getText() == '.':
            last = AST.AttributeNode(last, AST.StringNode(ctx.getChild(index+1).getText()))
            index += 2
        else:
            raise SyntaxError(f"expected '.' or '[' got {ctx.getChild(index).getText()}")
        

    return last # type: ignore
