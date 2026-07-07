from syntax_tree.ASTNodes import ASTNode , SequenceNode , BlockNode , AttributeNode , VarNode , StringNode , AssignmentNode , NumberNode

def FindFirstNodeOfType(Tree : ASTNode , TargetType : type):
    if isinstance(Tree , ASTNode) == False: return None

    if isinstance(Tree, TargetType):
        return Tree
    
    elif type(Tree) is BlockNode:
        return FindFirstNodeOfType(Tree.sequence , TargetType)
    elif type(Tree) is SequenceNode:
        for each_node in Tree.statements:
            result = FindFirstNodeOfType(each_node , TargetType)
            if result: return result
            
    return None