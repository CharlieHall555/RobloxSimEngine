import unittest
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))

from main import preprocess_lua_code, InputStream, LuaLexer, CommonTokenStream, LuaParser  # type: ignore
from syntax_tree.ASTBuilder import ASTBuilder
from syntax_tree.ASTNodes import (
    AssignmentNode, VarNode, NumberNode, OperatorNode, ExpressionNode, UnaryNode
)
from syntax_tree.ASTTraversal import FindFirstNodeOfType


class AllOperatorsTest(unittest.TestCase):

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

    def make_assignment(self, op, left=1, right=2):
        return AssignmentNode(
            VarNode("x"),
            ExpressionNode(
                NumberNode(left),
                NumberNode(right),
                OperatorNode(op)
            )
        )

    def make_unary_assignment(self, op, operand=1):
        return AssignmentNode(
            VarNode("x"),
            UnaryNode(
                NumberNode(operand),
                OperatorNode(op)
            )
        )

    def test_exponentiation(self):
        ast = self.parse("x = 1 ^ 2")
        self.assertEqual(str(self.make_assignment("^")), str(FindFirstNodeOfType(ast, AssignmentNode)))

    def test_unary_not(self):
        ast = self.parse("x = not 1")
        self.assertEqual(str(self.make_unary_assignment("not")), str(FindFirstNodeOfType(ast, AssignmentNode)))

    def test_unary_len(self):
        ast = self.parse("x = #1")
        self.assertEqual(str(self.make_unary_assignment("#")), str(FindFirstNodeOfType(ast, AssignmentNode)))

    def test_unary_minus(self):
        ast = self.parse("x = -1")
        self.assertEqual(str(self.make_unary_assignment("-")), str(FindFirstNodeOfType(ast, AssignmentNode)))

    def test_unary_bnot(self):
        ast = self.parse("x = ~1")
        self.assertEqual(str(self.make_unary_assignment("~")), str(FindFirstNodeOfType(ast, AssignmentNode)))

    def test_multiplication(self):
        ast = self.parse("x = 1 * 2")
        self.assertEqual(str(self.make_assignment("*")), str(FindFirstNodeOfType(ast, AssignmentNode)))

    def test_division(self):
        ast = self.parse("x = 1 / 2")
        self.assertEqual(str(self.make_assignment("/")), str(FindFirstNodeOfType(ast, AssignmentNode)))

    def test_modulo(self):
        ast = self.parse("x = 1 % 2")
        self.assertEqual(str(self.make_assignment("%")), str(FindFirstNodeOfType(ast, AssignmentNode)))

    def test_floor_div(self):
        ast = self.parse("x = 1 // 2")
        self.assertEqual(str(self.make_assignment("//")), str(FindFirstNodeOfType(ast, AssignmentNode)))

    def test_addition(self):
        ast = self.parse("x = 1 + 2")
        self.assertEqual(str(self.make_assignment("+")), str(FindFirstNodeOfType(ast, AssignmentNode)))

    def test_subtraction(self):
        ast = self.parse("x = 1 - 2")
        self.assertEqual(str(self.make_assignment("-")), str(FindFirstNodeOfType(ast, AssignmentNode)))

    def test_concat(self):
        ast = self.parse("x = 1 .. 2")
        self.assertEqual(str(self.make_assignment("..")), str(FindFirstNodeOfType(ast, AssignmentNode)))

    def test_less_than(self):
        ast = self.parse("x = 1 < 2")
        self.assertEqual(str(self.make_assignment("<")), str(FindFirstNodeOfType(ast, AssignmentNode)))

    def test_greater_than(self):
        ast = self.parse("x = 1 > 2")
        self.assertEqual(str(self.make_assignment(">")), str(FindFirstNodeOfType(ast, AssignmentNode)))

    def test_less_equal(self):
        ast = self.parse("x = 1 <= 2")
        self.assertEqual(str(self.make_assignment("<=")), str(FindFirstNodeOfType(ast, AssignmentNode)))

    def test_greater_equal(self):
        ast = self.parse("x = 1 >= 2")
        self.assertEqual(str(self.make_assignment(">=")), str(FindFirstNodeOfType(ast, AssignmentNode)))

    def test_not_equal(self):
        ast = self.parse("x = 1 ~= 2")
        self.assertEqual(str(self.make_assignment("~=")), str(FindFirstNodeOfType(ast, AssignmentNode)))

    def test_equal(self):
        ast = self.parse("x = 1 == 2")
        self.assertEqual(str(self.make_assignment("==")), str(FindFirstNodeOfType(ast, AssignmentNode)))

    def test_and(self):
        ast = self.parse("x = 1 and 2")
        self.assertEqual(str(self.make_assignment("and")), str(FindFirstNodeOfType(ast, AssignmentNode)))

    def test_or(self):
        ast = self.parse("x = 1 or 2")
        self.assertEqual(str(self.make_assignment("or")), str(FindFirstNodeOfType(ast, AssignmentNode)))


if __name__ == "__main__":
    unittest.main()
