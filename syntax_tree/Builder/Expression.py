from __future__ import annotations

from parser.LuaParserVisitor import LuaParserVisitor
from parser.LuaParser import LuaParser
import syntax_tree.ASTNodes as AST
from syntax_tree.ASTNodes import ASTNode, ExpressionNode, ExpressionBase , LiteralNode , IdentifierBase
import parser.LuaLexer as LuaLexer
import typing
from syntax_tree.Builder.Misc import build_bracket_or_dot

if typing.TYPE_CHECKING:
    from syntax_tree.ASTBuilder import ASTBuilder

def build_simple_expression(main : ASTBuilder , ctx : LuaParser.ExpContext) -> ExpressionBase:
    if ctx.number():
        return AST.NumberNode(ctx.getText())
    elif ctx.string():
        return AST.StringNode(ctx.getText()[1:-1])
    elif ctx.FALSE():
        return AST.BoolNode(False)
    elif ctx.TRUE():
        return AST.BoolNode(True)
    elif ctx.DDD():
        return AST.VarArgsNode()
    elif ctx.NIL():
        return AST.NilNode()
    else:
        raise SyntaxError
    
def build_unary_expression(main : ASTBuilder , ctx : LuaParser.ExpContext) -> ExpressionBase:
    op = ctx.getChild(0)
    exp = ctx.getChild(1)
    if op.getText() in ["not" , "#" , "-" , "~"]:
        return AST.UnaryNode(main.safeVisit(exp) , AST.OperatorNode(op.getText()))
    else:
        raise SyntaxError("unexpected symbol for unary expression")

valid_operators : typing.Set[str] = set(["+" , "-" , "/" , "*" ,  "//" , "%" , "^", ">" , "<" , ">=" , "<=" , "==" , "~=" ,  "and" , "or" , ".."])

def build_op_expression(main : ASTBuilder , ctx : LuaParser.ExpContext) -> ExpressionBase:
    exp1 , exp2 = ctx.exp()[0] , ctx.exp()[1]
    op = ctx.getChild(1)
    if op.getText() in valid_operators:
        return AST.ExpressionNode(
            main.safeVisit(exp1),
            main.safeVisit(exp2),
            AST.OperatorNode(op.getText())
        )
    else:
        raise SyntaxError

def build_expression(main : ASTBuilder , ctx : LuaParser.ExpContext) -> ExpressionBase | IdentifierBase:
    if ctx.prefixexp():
        return main.safeVisit(ctx.prefixexp())
    elif ctx.functiondef():
        return main.safeVisit(ctx.functiondef())
    elif ctx.tableconstructor():
        return main.safeVisit(ctx.tableconstructor())
    elif ctx.getChildCount() == 1:
        return build_simple_expression(main , ctx)
    elif ctx.getChildCount() == 2:
        return build_unary_expression(main , ctx)
    elif ctx.getChildCount() == 3:
        return build_op_expression(main , ctx)
    else:
        raise SyntaxError
        
    