import unittest
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))

from main import preprocess_lua_code, InputStream, LuaLexer , CommonTokenStream , LuaParser
from syntax_tree.ASTBuilder import ASTBuilder
from syntax_tree.ASTNodes import (
    VarNode, StringNode, NumberNode, FunctionCallNode, ArgsNode,
    AssignmentNode, AttributeNode
)
from syntax_tree.ASTTraversal import FindFirstNodeOfType

class FunctionCallTest(unittest.TestCase):

    def setUp(self):
        self.maxDiff = None

    def parse(self, code: str):
        code = preprocess_lua_code(code)
        input_stream = InputStream(code)
        lexer = LuaLexer(input_stream)
        token_stream = CommonTokenStream(lexer)
        parser = LuaParser(token_stream)
        parse_tree = parser.block()
        visitor = ASTBuilder()
        return visitor.visit(parse_tree)

    def test_simple_call(self):
        code = "f()"
        ast = self.parse(code)
        expected = FunctionCallNode(
            VarNode("f"),
            ArgsNode([])
        )
        actual = FindFirstNodeOfType(ast, FunctionCallNode)
        self.assertEqual(str(expected), str(actual))

    def test_call_with_args(self):
        code = "print(1, 2, 3)"
        ast = self.parse(code)
        expected = FunctionCallNode(
            VarNode("print"),
            ArgsNode([NumberNode(1), NumberNode(2), NumberNode(3)])
        )
        actual = FindFirstNodeOfType(ast, FunctionCallNode)
        self.assertEqual(str(expected), str(actual))

    def test_nested_call(self):
        code = "outer(inner(5))"
        ast = self.parse(code)
        expected = FunctionCallNode(
            VarNode("outer"),
            ArgsNode([
                FunctionCallNode(
                    VarNode("inner"),
                    ArgsNode([NumberNode(5)])
                )
            ])
        )
        actual = FindFirstNodeOfType(ast, FunctionCallNode)
        self.assertEqual(str(expected), str(actual))

    def test_call_with_string_arg(self):
        code = 'say("hello")'
        ast = self.parse(code)
        expected = FunctionCallNode(
            VarNode("say"),
            ArgsNode([StringNode("hello")])
        )
        actual = FindFirstNodeOfType(ast, FunctionCallNode)
        self.assertEqual(str(expected), str(actual))

    def test_method_call_colon(self):
        code = 'obj:method(123)'
        ast = self.parse(code)
        expected = FunctionCallNode(
            AttributeNode(VarNode("obj"), StringNode("method")),
            ArgsNode([NumberNode(123)])
        )
        actual = FindFirstNodeOfType(ast, FunctionCallNode)
        self.assertEqual(str(expected), str(actual))

    def test_function_call_assigned(self):
        code = "result = compute(9)"
        ast = self.parse(code)
        expected = AssignmentNode(
            VarNode("result"),
            FunctionCallNode(
                VarNode("compute"),
                ArgsNode([NumberNode(9)])
            )
        )
        actual = FindFirstNodeOfType(ast, AssignmentNode)
        self.assertEqual(str(expected), str(actual))

    def test_call_on_index(self):
        code = "obj['callback']()"
        ast = self.parse(code)
        expected = FunctionCallNode(
            AttributeNode(
                VarNode("obj"),
                StringNode("callback")
            ),
            ArgsNode([])
        )
        actual = FindFirstNodeOfType(ast, FunctionCallNode)
        self.assertEqual(str(expected), str(actual))

    def test_chained_function_call(self):
        code = "a().b()"
        ast = self.parse(code)
        expected = FunctionCallNode(
            AttributeNode(
                FunctionCallNode(
                    VarNode("a"),
                    ArgsNode([])
                ),
                StringNode("b")
            ),
            ArgsNode([])
        )
        actual = FindFirstNodeOfType(ast, FunctionCallNode)
        self.assertEqual(str(expected), str(actual))

if __name__ == "__main__":
    unittest.main()