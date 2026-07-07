import typing


class ASTNode:
    pass

    def __str__(self):
        return str(self.__class__.__name__) + ":" + str(self.__dict__)

    def __repr__(self):
        return self.__str__()
    
class BlockNode(ASTNode):
    sequence : "SequenceNode"
    def __init__(self , sequence : "SequenceNode"):
        super().__init__()
        self.sequence = sequence


class ForNode(ASTNode):
    iterator : "VarNode"
    start : typing.Union["ExpressionNode", "NumberNode"]
    step : typing.Union["ExpressionNode", "NumberNode"]
    end : typing.Union["ExpressionNode", "NumberNode"]
    block : "BlockNode"
    def __init__(self , iterator , start , step , end , block):
        self.block = block
        self.step = step
        self.start = start
        self.iterator = iterator
        self.end = end
        super().__init__()

class IfNode(ASTNode):
    condition : "ExpressionNode"
    then_block : "BlockNode"
    else_block : typing.Optional[typing.Union["BlockNode" , "IfNode"]]
    def __init__(self , condition : "ExpressionNode"  , then_block : "BlockNode" , else_block : typing.Optional[typing.Union["BlockNode" , "IfNode"]] = None):
        self.condition = condition
        self.then_block = then_block
        self.else_block = else_block
        super().__init__()    

class OperatorNode(ASTNode):
    value: str

    def __init__(self, value):
        super().__init__()
        self.value = value



# ----------- Expression Node-----------

class ExpressionBase(ASTNode):
    def __init__(self):
        pass

class ExpressionNode(ExpressionBase):
    exp1: typing.Union["ExpressionNode", "NumberNode" , "VarNode"]
    exp2: typing.Union["ExpressionNode", "NumberNode" , "VarNode"]
    op: "OperatorNode"

    def __init__(
        self,
        exp1: typing.Union["ExpressionNode", "NumberNode"],
        exp2: typing.Union["ExpressionNode", "NumberNode"],
        op: "OperatorNode"
    ):
        super().__init__()
        self.exp1 = exp1
        self.exp2 = exp2
        self.op = op

class UnaryNode(ExpressionBase):
    exp : typing.Union["ExpressionNode", "NumberNode" , "VarNode"]
    op : "OperatorNode"
    def __init__(self , exp : typing.Union["ExpressionNode", "NumberNode" , "VarNode"] , op : "OperatorNode"):
        self.exp = exp
        self.op = op
        super().__init__()

# ----------- Table Nodes -----------

class FieldNode(ASTNode):
    field_value : "ExpressionBase"
    field_name : typing.Optional["ExpressionBase"]
    def __init__(self , field_value : "ExpressionBase" , field_name: typing.Optional["ExpressionBase"]=None):
        self.field_value = field_value
        self.field_name = field_name
        super().__init__()

class TableConstructor(ExpressionBase):
    fields : typing.List["FieldNode"]
    def __init__(self , fields = []):
        self.fields = fields
        super().__init__()        

# ----------- Function Nodes -----------

class ArgsNode(ASTNode):
    args : typing.List[ExpressionBase]
    def __init__(self , args : typing.List[typing.Any] ):
        super().__init__()
        self.args = args

class FunctionDefinitionNode(ExpressionBase):
    name : typing.Optional["IdentifierBase"]
    body : BlockNode
    params : typing.List["VarNode"]
    local : bool
    def __init__(self, name : "VarNode", body : BlockNode, params : typing.List["VarNode"], local : bool = False ):
        self.name = name
        self.params = params
        self.body = body
        self.local = local

class FunctionCallNode(ExpressionBase):
    func_name : "IdentifierBase"
    args : "ArgsNode"
    def __init__(self, func_name : "IdentifierBase" , args : "ArgsNode"):
        self.func_name = func_name
        self.args = args

class MethodCallNode(FunctionCallNode):
    func_name : "AttributeNode"
    base : "ExpressionBase"
    args : "ArgsNode"
    def __init__(self, base : "ExpressionBase", func_name : "IdentifierBase" , args : "ArgsNode"):
        self.func_name = func_name
        self.args = args

# ----------- Literal Nodes -----------

class LiteralNode(ExpressionBase):
    def __init__(self):
        super().__init__()

class NilNode(LiteralNode):
    def __init__(self):
        super().__init__()

class NumberNode(LiteralNode):
    def __init__(self, value):
        super().__init__()
        self.value = float(value)

class StringNode(LiteralNode):
    def __init__(self, value):
        super().__init__()
        self.value = value

class BoolNode(LiteralNode):
    def __init__(self, value):
        super().__init__()
        self.value = value

# ---------------------------------

#------------ Identifer Nodes ---------------------

class IdentifierBase(ExpressionBase):
    def __init__(self):
        super().__init__()

class VarNode(IdentifierBase):
    def __init__(self, value):
        super().__init__()
        self.value = value

class AttributeName(IdentifierBase):
    value : ExpressionBase
    def __init__(self, value):
        super().__init__()
        self.value = value

class AttributeNode(IdentifierBase):
    base: typing.Union["AttributeNode", "VarNode"]
    property: typing.Union["ExpressionBase"]

    def __init__(self, base, property):
        super().__init__()
        self.base = base
        self.property = property

class AssignmentNode(ASTNode):
    target : "IdentifierBase"
    local : bool
    value : typing.Union["ExpressionNode" , "VarNode" , "NumberNode"]
    def __init__(self, target, value , local=False):
        super().__init__()
        self.local = local
        self.target = target
        self.value = value

class MultiAssignmentNode(ASTNode):
    targets : typing.List["IdentifierBase"]
    local : bool
    values : typing.List[typing.Union["ExpressionBase" , "IdentifierBase" , "LiteralNode"]]      
    def __init__(self, targets : typing.List["IdentifierBase"], values : typing.List[typing.Union["ExpressionBase" , "IdentifierBase" , "LiteralNode"]] , local=False):
        self.local = local
        self.targets = targets
        self.values = values


class MethodNode(ASTNode):
    base: typing.Union["AttributeNode", "VarNode"]
    function: "FunctionDefinitionNode"

    def __init__(self, base, function):
        super().__init__()
        self.base = base
        self.function = property

class SequenceNode(ASTNode):
    def __init__(self, statements):
        self.statements = statements

class WhileNode(ASTNode):
    block : "BlockNode"
    condition : "ExpressionBase"
    def __init__(self , condition : ExpressionBase , block : BlockNode):
        self.block = block
        self.condition = condition  
        super().__init__()

class RepeatNode(ASTNode):
    block : "BlockNode"
    condition : "ExpressionBase"
    def __init__(self , block : BlockNode , condition : "ExpressionBase"):
        self.block = block
        self.condition = condition  
        super().__init__()

class ReturnStatmentBase(ASTNode):
    def __init__(self):
        super().__init__()

class ReturnNode(ReturnStatmentBase):
    ExpressionList : typing.List[ExpressionBase]
    def __init__(self , ExpressionList : typing.List[ExpressionBase]):
        self.ExpressionList = ExpressionList
        super().__init__()

class BreakNode(ReturnStatmentBase):
    def __init__(self):
        super().__init__()
    

class ContinueNode(ReturnStatmentBase):
    def __init__(self):
        super().__init__()      

class VarArgsNode(ExpressionBase):
    def __init__(self):
        super().__init__()
