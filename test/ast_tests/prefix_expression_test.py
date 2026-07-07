import unittest
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))

from main import preprocess_lua_code, InputStream, LuaLexer , CommonTokenStream , LuaParser # type: ignore
from syntax_tree.ASTBuilder import ASTBuilder
from syntax_tree.ASTNodes import SequenceNode , BlockNode  , AttributeNode , VarNode , StringNode , AssignmentNode , NumberNode
from syntax_tree.ASTTraversal import FindFirstNodeOfType

class PrefixExpressionTest(unittest.TestCase):
    
    def setUp(self):
        self.maxDiff = None

    def test_one(self):
        code = preprocess_lua_code("x.y.z = 10")
        input_stream = InputStream(code)
        lexer = LuaLexer(input_stream)
        token_stream = CommonTokenStream(lexer)
        parser = LuaParser(token_stream)
        parse_tree = parser.block()
        visitor = ASTBuilder()
        
        ast = visitor.visit(parse_tree)

        expected = AssignmentNode(
            AttributeNode(
                AttributeNode(
                    VarNode("x"), 
                    StringNode("y")
                ), 
                StringNode("z")), 
            NumberNode(10))


        AssNode = FindFirstNodeOfType(ast , AssignmentNode)
        self.assertEqual(str(expected) , str(AssNode))

    def test_two(self):
        code = preprocess_lua_code("person['name'] = 42")
        input_stream = InputStream(code)
        lexer = LuaLexer(input_stream)
        token_stream = CommonTokenStream(lexer)
        parser = LuaParser(token_stream)
        parse_tree = parser.block()
        visitor = ASTBuilder()
        ast = visitor.visit(parse_tree)

        expected = AssignmentNode(
            AttributeNode(
                VarNode("person"),
                StringNode("name")
            ),
            NumberNode(42)
        )

        AssNode = FindFirstNodeOfType(ast, AssignmentNode)
        self.assertEqual(str(expected), str(AssNode))

    def test_three(self):
        code = preprocess_lua_code("a.b['c'].d = 5")
        input_stream = InputStream(code)
        lexer = LuaLexer(input_stream)
        token_stream = CommonTokenStream(lexer)
        parser = LuaParser(token_stream)
        parse_tree = parser.block()
        visitor = ASTBuilder()
        ast = visitor.visit(parse_tree)

        expected = AssignmentNode(
            AttributeNode(
                AttributeNode(
                    AttributeNode(
                        VarNode("a"),
                        StringNode("b")
                    ),
                    StringNode("c")
                ),
                StringNode("d")
            ),
            NumberNode(5)
        )

        AssNode = FindFirstNodeOfType(ast, AssignmentNode)
        self.assertEqual(str(expected), str(AssNode))

    def test_parenthesized_prefix_expression(self):
        code = preprocess_lua_code("(x).y['z'] = 100")
        input_stream = InputStream(code)
        lexer = LuaLexer(input_stream)
        token_stream = CommonTokenStream(lexer)
        parser = LuaParser(token_stream)
        parse_tree = parser.block()
        visitor = ASTBuilder()
        ast = visitor.visit(parse_tree)

        expected = AssignmentNode(
            AttributeNode(
                AttributeNode(
                    VarNode("x"),
                    
                    StringNode("y")
                ),
                StringNode("z")
            ),
            NumberNode(100)
        )

        AssNode = FindFirstNodeOfType(ast, AssignmentNode)
        self.assertEqual(str(expected), str(AssNode))

    def test_function_call_prefix_expression(self):
        code = preprocess_lua_code("getObj().field = 123")
        input_stream = InputStream(code)
        lexer = LuaLexer(input_stream)
        token_stream = CommonTokenStream(lexer)
        parser = LuaParser(token_stream)
        parse_tree = parser.block()
        visitor = ASTBuilder()
        ast = visitor.visit(parse_tree)

        from syntax_tree.ASTNodes import FunctionCallNode, ArgsNode

        expected = AssignmentNode(
            AttributeNode(
                FunctionCallNode(
                    VarNode("getObj"),
                    ArgsNode([])
                ),
                StringNode("field")
            ),
            NumberNode(123)
        )

        AssNode = FindFirstNodeOfType(ast, AssignmentNode)
        self.assertEqual(str(expected), str(AssNode))


if __name__ == "__main__":
    unittest.main()
