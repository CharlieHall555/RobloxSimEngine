from parser.LuaParserVisitor import LuaParserVisitor
from parser.LuaParser import LuaParser
import syntax_tree.ASTNodes as AST
from syntax_tree.ASTNodes import ASTNode
import parser.LuaLexer as LuaLexer
import typing

#---------- SUBBUILDER IMPORTS -----------
# 
from syntax_tree.Builder.PrefixExpression import build_prefix_expression
from syntax_tree.Builder.IfExpression import build_if
from syntax_tree.Builder.While import build_while
from syntax_tree.Builder.Repeat import build_repeat
from syntax_tree.Builder.Expression import build_expression
from syntax_tree.Builder.Return import build_return_statement
from syntax_tree.Builder.FunctionCall import build_function_call
from syntax_tree.Builder.Assignment import build_assignment_attr_list, build_assignment_exp_list
from syntax_tree.Builder.Table import build_table, build_field_list, build_field
from syntax_tree.Builder.Do import build_do
from syntax_tree.Builder.FunctionDef import build_anon_function

class ASTBuilder(LuaParserVisitor):
    visit_count : int
    max_visits : int
    def __init__(self , max_visits:int=1000):
        self.visit_count = 0
        self.max_visits = max_visits
        super().__init__()

    def safeVisit(self , ctx):
        if self.visit_count > self.max_visits:
            raise SyntaxError("max visit count exceeded")
        else:
            self.visit_count += 1
            return self.visit(ctx)

    def visitStart_(self, ctx):
        return self.safeVisit(ctx.chunk())

    def visitChunk(self, ctx : LuaParser.ChunkContext) -> ASTNode:
        return self.safeVisit(ctx.block())
    

    def visitBlock(self, ctx : LuaParser.BlockContext):
        statments = []

        for i in range(0 , ctx.getChildCount()):
            result = self.safeVisit(ctx.getChild(i))
            if result:
                statments.append(result)

        return AST.BlockNode(AST.SequenceNode(statments))
        
    def visitAttnamelist(self, ctx) -> typing.List[AST.VarNode]:

        o_list : typing.List[AST.VarNode] = []

        for i in range(0 , ctx.getChildCount() , 3):

            var_name : str = ctx.getChild(i).getText()
            o_list.append(AST.VarNode(var_name))

        return o_list
    
    def visitRetstat(self, ctx):
        return build_return_statement(self , ctx)
    
    def visitStat(self, ctx : LuaParser.StatContext):
        #varlist '=' explist

        if ctx.varlist() and ctx.EQ() and ctx.explist():
            return build_assignment_exp_list(self , ctx)
        #funciton definition
        elif ctx.getChildCount() == 1 and ctx.getText() == "break":
            return AST.BreakNode()
        elif ctx.LOCAL() and ctx.FUNCTION() and ctx.NAME() and ctx.funcbody():
            function_name : AST.VarNode
            params : typing.List[AST.VarNode]
            function_body : AST.BlockNode

            function_name = AST.VarNode(ctx.NAME().getText())
            params , function_body = self.safeVisit(ctx.funcbody())
            return AST.FunctionDefinitionNode(function_name , function_body , params , True)
        
        elif ctx.funcname() and ctx.funcbody():
            function_name : AST.VarNode
            params : typing.List[AST.VarNode]
            function_body : AST.BlockNode

            function_name = self.safeVisit(ctx.funcname())
            params , function_body = self.safeVisit(ctx.funcbody())
            return AST.FunctionDefinitionNode(function_name , function_body , params , False)
  
        elif ctx.WHILE():
            return build_while(self ,  ctx)
        
        elif ctx.REPEAT():
            return build_repeat(self , ctx)

        #function call
        elif ctx.functioncall():
            self.safeVisit(ctx.functioncall())

        #'local' attnamelist ('=' explist)?  
        elif ctx.LOCAL() and ctx.attnamelist():
            return build_assignment_attr_list(self , ctx)
        elif ctx.FOR() and ctx.NAME() and ctx.exp() and ctx.COMMA() and ctx.DO() and ctx.block() and ctx.END():
            return self.build_for(ctx)
        elif ctx.IF():
            return build_if(self , ctx)
        elif ctx.DO():
            return build_do(self , ctx)

    

        return super().visitStat(ctx)
    
    def visitExp(self, ctx : LuaParser.ExpContext):
        return build_expression(self , ctx)

    def visitVar(self, ctx : LuaParser.VarContext):
        if ctx.getChildCount() == 1:
            # NAME case
            if ctx.NAME(): 
                return AST.VarNode(ctx.getText())
        
        elif ctx.prefixexp():
            attr = None
            # prefixexp '[' exp ']' case
            if ctx.exp():
                attr = self.safeVisit(ctx.exp())
            # prefixexp '.' NAME case
            else:
                attr = AST.StringNode(ctx.getChild(2).getText())

            return AST.AttributeNode(
                self.safeVisit(ctx.prefixexp()),
                attr
            )

    def visitFunctiondef(self, ctx : LuaParser.FunctiondefContext):
        return build_anon_function(self , ctx)


    def visitFunctioncall(self, ctx) -> AST.FunctionCallNode:
    
        return build_function_call(self , ctx)

    def visitArgs(self, ctx) -> AST.ArgsNode:
        """
        args
            : '(' explist? ')'
            | tableconstructor
            | string
            ;
        """

        args : AST.ArgsNode = AST.ArgsNode([])

        if ctx.getChild(0).getText() == '(':
            if ctx.explist():
                expressions : typing.List[AST.ExpressionBase] = self.safeVisit(ctx.explist())
                args = AST.ArgsNode(expressions)
        
        return args

    def visitTableconstructor(self, ctx : LuaParser.TableconstructorContext):
        return build_table(self , ctx)

    def visitFieldlist(self, ctx):
        return build_field_list(self , ctx)

    def visitField(self, ctx):
        return build_field(self , ctx)

    def visitVarlist(self, ctx : LuaParser.VarlistContext) -> typing.List[AST.VarNode]:
        vars = ctx.var()
        output = []
        if vars:
            for var in vars:
                output.append(self.safeVisit(var))
        return output

    def visitFuncname(self, ctx : LuaParser.FuncnameContext) -> typing.Union[AST.VarNode , AST.MethodNode , AST.AttributeNode]:
        if ctx.getChildCount() == 1:
            return AST.VarNode(ctx.getText())

        return super().visitFuncname(ctx)

    def visitFuncbody(self, ctx : LuaParser.FuncbodyContext) -> typing.Tuple[typing.List[AST.VarNode] , AST.BlockNode]:
        name_list : typing.List[AST.VarNode] 
        if ctx.parlist():
            name_list = self.safeVisit(ctx.parlist())
        else:
            name_list = []
        body : AST.BlockNode = self.safeVisit(ctx.block())

        return name_list , body

    def visitParlist(self, ctx : LuaParser.ParlistContext):
        if ctx.getChildCount() == 1:
            if ctx.namelist():
                return self.safeVisit(ctx.namelist())
            elif ctx.getText() == "...":
                return [AST.VarArgsNode()]
        elif ctx.getChildCount() == 3:
            return self.safeVisit(ctx.namelist()) + [AST.VarArgsNode()]
        else:
            return []

    def visitNamelist(self, ctx : LuaParser.NamelistContext) -> typing.List[AST.VarNode]:
        output = []

        for i in range(0 , ctx.getChildCount() , 2):
            output.append(AST.VarNode(ctx.getChild(i).getText()))

        return output

    def visitExplist(self, ctx):
        exps = ctx.exp()
        output = []
        if exps:
            for exp in exps:
                output.append(self.safeVisit(exp))
        return output

    def visitPrefixexp(self, ctx : LuaParser.PrefixexpContext):
        return build_prefix_expression(self , ctx)

   
    def build_for(self , ctx : LuaParser.StatContext) -> AST.ForNode:
        """Grammar: 'for' namelist 'in' explist 'do' block 'end'"""
        iterator : AST.VarNode = AST.VarNode(ctx.NAME().getText())
        start : typing.Union[AST.ExpressionNode | AST.NumberNode] = self.safeVisit(ctx.exp(0))
        end : typing.Union[AST.ExpressionNode | AST.NumberNode]  = self.safeVisit(ctx.exp(1))
        step : typing.Union[AST.ExpressionNode | AST.NumberNode] 
        if ctx.exp(2):
            step = self.safeVisit(ctx.exp(2))
        else:
            step = AST.NumberNode(1)

        return AST.ForNode(
            iterator,
            start,
            step,
            end,
            self.safeVisit(ctx.block(0))
        )
                
                

