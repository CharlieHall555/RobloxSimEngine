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

def build_simple_if(main : ASTBuilder , ctx : LuaParser.StatContext) -> AST.IfNode:
        """Grammar :'if' exp 'then' block 'end'"""
        condition : AST.ExpressionNode = main.safeVisit(ctx.getChild(1))
        block : AST.BlockNode = main.safeVisit(ctx.getChild(3))
        
        root : AST.IfNode = AST.IfNode(condition , block)

        return root
    

def build_if_elif_else(main : ASTBuilder , ctx : LuaParser.StatContext) -> AST.IfNode:
    """Grammar : 'if' exp 'then' block ('elseif' exp 'then' block)* ('else' block)? 'end'"""
    condition : AST.ExpressionNode 
    block : AST.BlockNode 
    root : AST.IfNode
    current : AST.IfNode 
    new : typing.Optional[AST.IfNode]

    condition = main.safeVisit(ctx.getChild(1))
    block = main.safeVisit(ctx.getChild(3))
    current = AST.IfNode(condition , block)
    root = current
    
    for i in range(4 , ctx.getChildCount() , 4):
        if ctx.getChild(i).getText() == "else":
            block = main.safeVisit(ctx.getChild(i + 1))
            current.else_block = block
            break
        else:
            condition = main.safeVisit(ctx.getChild(i+1))
            block = main.safeVisit(ctx.getChild(i+3))
            new = AST.IfNode(condition , block)
            current.else_block = new
            current = new
                
    return root

def build_if_else(main : ASTBuilder , ctx : LuaParser.StatContext) -> AST.IfNode:

    condition : AST.ExpressionNode 
    thenblock : AST.BlockNode 
    elseblock : AST.BlockNode 

    condition = main.safeVisit(ctx.getChild(1))
    thenblock = main.safeVisit(ctx.getChild(3))
    elseblock = main.safeVisit(ctx.getChild(5)) 

    return AST.IfNode(condition , thenblock , elseblock)

def build_if_elseif(main : ASTBuilder , ctx : LuaParser.StatContext) -> AST.IfNode:
    """Grammar :'if' exp 'then' block ('elseif' exp 'then' block)* 'end' """
    condition : AST.ExpressionNode 
    block : AST.BlockNode 
    root : AST.IfNode
    current : AST.IfNode 
    new : typing.Optional[AST.IfNode]

    condition = main.safeVisit(ctx.getChild(1))
    block = main.safeVisit(ctx.getChild(3))
    current = AST.IfNode(condition , block)
    root = current
    
    for i in range(4 , ctx.getChildCount() , 4):

        if ctx.getChild(i).getText() == "end":
            break
        else:
            condition = main.safeVisit(ctx.getChild(i+1))
            block = main.safeVisit(ctx.getChild(i+3))
            new = AST.IfNode(condition , block)
            current.else_block = new
            current = new

    return root

def build_if(main : ASTBuilder , ctx : LuaParser.StatContext):
    if ctx.IF() and ctx.THEN() and ctx.ELSEIF() and ctx.ELSE() and ctx.END():
        return build_if_elif_else(main , ctx)
    elif ctx.IF() and ctx.THEN() and ctx.ELSEIF() and ctx.END():
        return build_if_elseif(main , ctx)
    elif ctx.IF() and ctx.THEN() and ctx.ELSE() and ctx.END():
        return build_if_else(main , ctx)
    elif ctx.IF() and ctx.THEN() and ctx.END():
        return build_simple_if(main , ctx)