import unittest
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))

from main import preprocess_lua_code, InputStream, LuaLexer, CommonTokenStream, LuaParser  # type: ignore
from syntax_tree.ASTBuilder import ASTBuilder
from syntax_tree.ASTNodes import (
    BlockNode, SequenceNode, AssignmentNode, MultiAssignmentNode,
    VarNode, NumberNode
)
from syntax_tree.ASTTraversal import FindFirstNodeOfType


class AssignmentTest(unittest.TestCase):

    def setUp(self):
        self.maxDiff = None

    def parse(self, code):
        code = preprocess_lua_code(code)
        input_stream = InputStream(code)
        lexer = LuaLexer(input_stream)
        token_stream = CommonTokenStream(lexer)
        parser = LuaParser(token_stream)
        parse_tree = parser.block()
        visitor = ASTBuilder()
        return visitor.visit(parse_tree)

    def test_local_single_assignment(self):
        code = "local x = 20"
        ast = self.parse(code)
        expected = AssignmentNode(
            VarNode("x"),
            NumberNode(20.0),
            local=True
        )
        actual = FindFirstNodeOfType(ast, AssignmentNode)
        self.assertEqual(str(expected), str(actual))

    def test_global_single_assignment(self):
        code = "x = 20"
        ast = self.parse(code)
        expected = AssignmentNode(
            VarNode("x"),
            NumberNode(20.0),
            local=False
        )
        actual = FindFirstNodeOfType(ast, AssignmentNode)
        self.assertEqual(str(expected), str(actual))

    def test_local_multi_assignment(self):
        code = "local x, y = 10, 20"
        ast = self.parse(code)
        expected = MultiAssignmentNode(
            targets=[VarNode("x"), VarNode("y")],
            values=[NumberNode(10.0), NumberNode(20.0)],
            local=True
        )
        actual = FindFirstNodeOfType(ast, MultiAssignmentNode)
        self.assertEqual(str(expected), str(actual))

    def test_global_multi_assignment(self):
        code = "x, y = 10, 20"
        ast = self.parse(code)
        expected = MultiAssignmentNode(
            targets=[VarNode("x"), VarNode("y")],
            values=[NumberNode(10.0), NumberNode(20.0)],
            local=False
        )
        actual = FindFirstNodeOfType(ast, MultiAssignmentNode)
        self.assertEqual(str(expected), str(actual))


if __name__ == "__main__":
    unittest.main()
