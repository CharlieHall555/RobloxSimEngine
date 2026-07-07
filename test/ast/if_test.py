import unittest
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))

from main import preprocess_lua_code, InputStream, LuaLexer , CommonTokenStream , LuaParser  # type: ignore
from syntax_tree.ASTBuilder import ASTBuilder
from syntax_tree.ASTNodes import (
    BlockNode, SequenceNode, IfNode, ExpressionNode, OperatorNode,
    VarNode, AssignmentNode, NumberNode, StringNode
)
from syntax_tree.ASTTraversal import FindFirstNodeOfType


class IfStatementTest(unittest.TestCase):

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

    def test_basic_if_else(self):
        code = """
        if a > b then
            result = a - b
        else
            result = a + b
        end
        """
        ast = self.parse(code)

        expected = BlockNode(
            SequenceNode([
                IfNode(
                    ExpressionNode(VarNode("a"), VarNode("b"), OperatorNode(">")),
                    BlockNode(
                        SequenceNode([
                            AssignmentNode(
                                VarNode("result"),
                                ExpressionNode(VarNode("a"), VarNode("b"), OperatorNode("-")),
                                local=False
                            )
                        ])
                    ),
                    BlockNode(
                        SequenceNode([
                            AssignmentNode(
                                VarNode("result"),
                                ExpressionNode(VarNode("a"), VarNode("b"), OperatorNode("+")),
                                local=False
                            )
                        ])
                    )
                )
            ])
        )

        self.assertEqual(str(expected), str(ast))

    def test_if_elseif_else_chain(self):
        code = """
        if a > b then
            result = a - b
        elseif a < b then
            result = c
        else
            result = "a"
        end
        """
        ast = self.parse(code)

        expected = BlockNode(
            SequenceNode([
                IfNode(
                    ExpressionNode(VarNode("a"), VarNode("b"), OperatorNode(">")),
                    BlockNode(
                        SequenceNode([
                            AssignmentNode(
                                VarNode("result"),
                                ExpressionNode(VarNode("a"), VarNode("b"), OperatorNode("-")),
                                local=False
                            )
                        ])
                    ),
                    IfNode(
                        ExpressionNode(VarNode("a"), VarNode("b"), OperatorNode("<")),
                        BlockNode(
                            SequenceNode([
                                AssignmentNode(
                                    VarNode("result"),
                                    VarNode("c"),
                                    local=False
                                )
                            ])
                        ),
                        BlockNode(
                            SequenceNode([
                                AssignmentNode(
                                    VarNode("result"),
                                    StringNode("a"),
                                    local=False
                                )
                            ])
                        )
                    )
                )
            ])
        )

        self.assertEqual(str(expected), str(ast))

    def test_multiple_if_blocks(self):
        code = """
        if a > b then
            result = a - b
        else
            result = a + b
        end

        if a > b then
            result = a - b
        elseif a < b then
            result = c
        else
            result = "a"
        end
        """
        ast = self.parse(code)

        expected = BlockNode(
            SequenceNode([
                IfNode(
                    ExpressionNode(VarNode("a"), VarNode("b"), OperatorNode(">")),
                    BlockNode(
                        SequenceNode([
                            AssignmentNode(
                                VarNode("result"),
                                ExpressionNode(VarNode("a"), VarNode("b"), OperatorNode("-")),
                                local=False
                            )
                        ])
                    ),
                    BlockNode(
                        SequenceNode([
                            AssignmentNode(
                                VarNode("result"),
                                ExpressionNode(VarNode("a"), VarNode("b"), OperatorNode("+")),
                                local=False
                            )
                        ])
                    )
                ),
                IfNode(
                    ExpressionNode(VarNode("a"), VarNode("b"), OperatorNode(">")),
                    BlockNode(
                        SequenceNode([
                            AssignmentNode(
                                VarNode("result"),
                                ExpressionNode(VarNode("a"), VarNode("b"), OperatorNode("-")),
                                local=False
                            )
                        ])
                    ),
                    IfNode(
                        ExpressionNode(VarNode("a"), VarNode("b"), OperatorNode("<")),
                        BlockNode(
                            SequenceNode([
                                AssignmentNode(
                                    VarNode("result"),
                                    VarNode("c"),
                                    local=False
                                )
                            ])
                        ),
                        BlockNode(
                            SequenceNode([
                                AssignmentNode(
                                    VarNode("result"),
                                    StringNode("a"),
                                    local=False
                                )
                            ])
                        )
                    )
                )
            ])
        )

        self.assertEqual(str(expected), str(ast))


if __name__ == "__main__":
    unittest.main()
