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

def build_assignment_exp_list(main : ASTBuilder , ctx : LuaParser.StatContext) -> typing.Union[AST.AssignmentNode , AST.MultiAssignmentNode]:
    
    var_list : typing.List[AST.IdentifierBase] = main.safeVisit(ctx.varlist())
    exp_list : typing.List[AST.ExpressionBase] = main.safeVisit(ctx.explist())
    
    if len(var_list) == 1 and len(exp_list) == 1:
        return AST.AssignmentNode(var_list[0] , exp_list[0] , False)
    else:
        return AST.MultiAssignmentNode(
             var_list,
             exp_list,
             False
        )
    

def build_assignment_attr_list(main : ASTBuilder , ctx : LuaParser.StatContext) -> typing.Union[AST.AssignmentNode , AST.MultiAssignmentNode]:
        assignments : typing.List[AST.AssignmentNode] = [] 
        var_list : typing.List[AST.IdentifierBase] = main.safeVisit(ctx.attnamelist())
        exp_list : typing.List[AST.ExpressionBase] = main.safeVisit(ctx.explist())

        if len(var_list) == 1 and len(exp_list) == 1:
            return AST.AssignmentNode(var_list[0] , exp_list[0] , True)
        else:
            return AST.MultiAssignmentNode(
                var_list,
                exp_list,
                True
            )
        