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

def build_table(main : ASTBuilder , ctx : LuaParser.TableconstructorContext):
    if ctx.fieldlist():
        return AST.TableConstructor(main.safeVisit(ctx.fieldlist()))
    else:
        return AST.TableConstructor([])

def build_field_list(main : ASTBuilder , ctx : LuaParser.FieldlistContext):
    field_list : typing.List[AST.FieldNode] = []

    for each_field in ctx.field():
        field_list.append(build_field(main , each_field))

    return field_list

def build_field(main : ASTBuilder , ctx : LuaParser.FieldContext):

    if ctx.exp() and ctx.getChildCount() == 1:
        return AST.FieldNode(main.safeVisit(ctx.getChild(0)))
    elif ctx.NAME() and ctx.EQ() and ctx.exp():
        return AST.FieldNode(main.safeVisit(ctx.getChild(2)) , AST.StringNode(ctx.getChild(0).getText()))
    elif ctx.getChild(0).getText() == "[" and ctx.exp():
        return AST.FieldNode(main.safeVisit(ctx.getChild(4)) , main.safeVisit(ctx.getChild(1)))
    else:
        raise SyntaxError