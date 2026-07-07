import unittest
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))) 

from main import preprocess_lua_code, InputStream, LuaLexer, CommonTokenStream, LuaParser # type: ignore
from syntax_tree.ASTBuilder import ASTBuilder
from syntax_tree.ASTNodes import (
    BlockNode, SequenceNode, AssignmentNode, VarNode,
    NumberNode, ExpressionNode, OperatorNode, WhileNode
)
from syntax_tree.ASTTraversal import FindFirstNodeOfType


class WhileLoopTest(unittest.TestCase):
    def setUp(self):
        self.maxDiff = None

    def test_basic_while_loop(self):
        code = preprocess_lua_code("""
        local total = 0
        while total == 0 do
            total = total + 1
            total = total + 2
        end
        """)
        input_stream = InputStream(code)
        lexer = LuaLexer(input_stream)
        token_stream = CommonTokenStream(lexer)
        parser = LuaParser(token_stream)
        parse_tree = parser.block()
        visitor = ASTBuilder()
        ast = visitor.visit(parse_tree)

        expected = WhileNode(
            condition=ExpressionNode(
                exp1=VarNode("total"),
                exp2=NumberNode(0),
                op=OperatorNode("==")
            ),
            block=BlockNode(
                SequenceNode([
                    AssignmentNode(
                        VarNode("total"),
                        ExpressionNode(
                            exp1=VarNode("total"),
                            exp2=NumberNode(1),
                            op=OperatorNode("+")
                        )
                    ),
                    AssignmentNode(
                        VarNode("total"),
                        ExpressionNode(
                            exp1=VarNode("total"),
                            exp2=NumberNode(2),
                            op=OperatorNode("+")
                        )
                    )
                ])
            )
        )

        while_node = FindFirstNodeOfType(ast, WhileNode)
        self.assertEqual(str(expected), str(while_node))


if __name__ == "__main__":
    unittest.main()
