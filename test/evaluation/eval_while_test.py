import unittest
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))

from main import run
from syntax_tree.ASTBuilder import ASTBuilder
from syntax_tree.ASTNodes import (
    AssignmentNode, VarNode, NumberNode, OperatorNode, ExpressionNode, UnaryNode
)

class EvalWhileLoopTest(unittest.TestCase):

    def test_simple_while_loop(self):
        code = """
        x = 0
        while x < 5 do
            x = x + 1
        end
        """
        success , message , state = run(code)
        memory_state = state.memory[0]
        self.assertEqual(memory_state.get("x"), 5)

    def test_while_loop_with_false_condition(self):
        code = """
        x = 0
        while false do
            x = x + 1
        end
        """
        success , message , state = run(code)
        memory_state = state.memory[0]
        self.assertEqual(memory_state.get("x"), 0)

    def test_while_loop_exact_end_condition(self):
        code = """
        x = 0
        while x ~= 3 do
            x = x + 1
        end
        """
        success , message , state = run(code)
        memory_state = state.memory[0]
        self.assertEqual(memory_state.get("x"), 3)

    def test_nested_while_loops(self):
        code = """
        count = 0
        x = 0
        while x < 3 do
            local y = 0
            while y < 3 do
                count = count + 1
                y = y + 1
            end
            x = x + 1
        end
        """
        success , message , state = run(code)
        memory_state = state.memory[0]
        self.assertEqual(memory_state.get("x"), 3)
        self.assertEqual(memory_state.get("count"), 9)
        self.assertIsNone(memory_state.get("y"))

    def test_while_loop_with_expression_condition(self):
        code = """
        x = 0
        y = 0
        while x < 5 do
            local y = 0
            x = x + 1
            y = y + 1
        end
        """
        success , message , state = run(code)
        memorty_state = state.memory[0]
        self.assertEqual(memorty_state.get("x"), 5)
        self.assertEqual(memorty_state.get("y"), 0)
