import unittest
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))

from main import run
from syntax_tree.ASTBuilder import ASTBuilder
from syntax_tree.ASTNodes import (
    AssignmentNode, VarNode, NumberNode, OperatorNode, ExpressionNode, UnaryNode
)

class EvalIfStatementTest(unittest.TestCase):

    def test_if_true_branch(self):
        code = """
        if true then
            x = 10
        end
        """
        success , message , state = run(code)
        memory_state : dict = state.memory[0]
        self.assertEqual(memory_state.get("x"), 10)

    def test_if_false_branch(self):
        code = """
        if false then
            x = 10
        end
        """
        success , message , state = run(code)
        memory_state : dict = state.memory[0]
        self.assertIsNone(memory_state.get("x"))

    def test_if_else_true_branch(self):
        code = """
        if true then
            x = 5
        else
            x = 10
        end
        """
        success , message , state = run(code)
        memory_state : dict = state.memory[0]
        self.assertEqual(memory_state.get("x"), 5)

    def test_if_else_false_branch(self):
        code = """
        if false then
            x = 5
        else
            x = 10
        end
        """
        success , message , state = run(code)
        memory_state : dict = state.memory[0]
        self.assertEqual(memory_state.get("x"), 10)

    def test_if_with_expression_condition(self):
        code = """
        a = 3
        b = 2
        if a > b then
            x = 100
        end
        """
        success , message , state = run(code)
        memory_state : dict = state.memory[0]
        self.assertEqual(memory_state.get("a"), 3)
        self.assertEqual(memory_state.get("b"), 2)
        self.assertEqual(memory_state.get("x"), 100)

    def test_if_elseif_else(self):
        code = """
        a = 3
        if a == 0 then
            x = 10
        elseif a == 3 then
            x = 20
        else
            x = 30
        end
        """
        success , message , state = run(code)
        memory_state : dict = state.memory[0]
        self.assertEqual(memory_state.get("a"), 3)
        self.assertEqual(memory_state.get("x"), 20)

    def test_nested_if(self):
        code = """
        if true then
            if 1 < 2 then
                x = 99
            end
        end
        """
        success , message , state = run(code)
        memory_state : dict = state.memory[0]
        self.assertEqual(memory_state.get("x"), 99)
