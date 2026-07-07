import unittest
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))

from main import preprocess_lua_code, InputStream, LuaLexer , CommonTokenStream , LuaParser  # type: ignore
from syntax_tree.ASTBuilder import ASTBuilder
from syntax_tree.ASTNodes import (
    BlockNode,
    SequenceNode,
    AssignmentNode,
    VarNode,
    NumberNode,
    RepeatNode,
    ExpressionNode,
    OperatorNode
)
from syntax_tree.ASTTraversal import FindFirstNodeOfType

class RepeatStructureTest(unittest.TestCase):

    def setUp(self):
        self.maxDiff = None

    def test_repeat_until_no_body(self):
        code = preprocess_lua_code("""
        local x = 1
        repeat
        until x > 3
        """)
        input_stream = InputStream(code)
        lexer = LuaLexer(input_stream)
        token_stream = CommonTokenStream(lexer)
        parser = LuaParser(token_stream)
        parse_tree = parser.block()
        visitor = ASTBuilder()
        ast = visitor.visit(parse_tree)

        expected = BlockNode(
            SequenceNode([
                AssignmentNode(
                    local=True,
                    target=VarNode("x"),
                    value=NumberNode(1.0)
                ),
                RepeatNode(
                    block=BlockNode(
                        SequenceNode([])
                    ),
                    condition=ExpressionNode(
                        exp1=VarNode("x"),
                        exp2=NumberNode(3.0),
                        op=OperatorNode(">")
                    )
                )
            ])
        )

        self.assertEqual(str(ast), str(expected))

    def test_repeat_until_with_nested_repeat(self):
        code = preprocess_lua_code("""
        local a = 0
        repeat
            repeat
                a = a + 1
            until a > 1
            a = a + 2
        until a > 10
        """)
        input_stream = InputStream(code)
        lexer = LuaLexer(input_stream)
        token_stream = CommonTokenStream(lexer)
        parser = LuaParser(token_stream)
        parse_tree = parser.block()
        visitor = ASTBuilder()
        ast = visitor.visit(parse_tree)

        outer_repeat = FindFirstNodeOfType(ast, RepeatNode)
        self.assertIsNotNone(outer_repeat)
        self.assertIsInstance(outer_repeat.block, BlockNode)
        self.assertIsInstance(outer_repeat.condition, ExpressionNode)

    def test_repeat_until_boolean_condition(self):
        code = preprocess_lua_code("""
        local done = false
        repeat
            done = true
        until done
        """)
        input_stream = InputStream(code)
        lexer = LuaLexer(input_stream)
        token_stream = CommonTokenStream(lexer)
        parser = LuaParser(token_stream)
        parse_tree = parser.block()
        visitor = ASTBuilder()
        ast = visitor.visit(parse_tree)

        repeat_node = FindFirstNodeOfType(ast, RepeatNode)
        self.assertEqual(str(repeat_node.condition), str(VarNode("done")))

    def test_repeat_until_complex_condition(self):
        code = preprocess_lua_code("""
        local x = 0
        repeat
            x = x + 1
        until x * 2 >= 10
        """)
        input_stream = InputStream(code)
        lexer = LuaLexer(input_stream)
        token_stream = CommonTokenStream(lexer)
        parser = LuaParser(token_stream)
        parse_tree = parser.block()
        visitor = ASTBuilder()
        ast = visitor.visit(parse_tree)

        repeat_node = FindFirstNodeOfType(ast, RepeatNode)
        self.assertEqual(repeat_node.condition.op.value, ">=")
        self.assertIsInstance(repeat_node.condition.exp1, ExpressionNode)
        self.assertEqual(repeat_node.condition.exp2.value, 10.0)



if __name__ == "__main__":
    unittest.main()
