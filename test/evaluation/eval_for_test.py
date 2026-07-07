import unittest
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))

from main import run
from syntax_tree.ASTBuilder import ASTBuilder
from syntax_tree.ASTNodes import (
    AssignmentNode, VarNode, NumberNode, OperatorNode, ExpressionNode, UnaryNode
)

class EvalForLoopTest(unittest.TestCase):

    def test_simple_loop_count(self):
        code = """
        sum = 0
        for i = 1, 3 do
            sum = sum + i
        end
        """
        success , message , state = run(code)
        memory_state : dict = state.memory[0]
        self.assertEqual(memory_state.get("sum"), 6)

    def test_loop_with_step(self):
        code = """
        sum = 0
        for i = 1, 5, 2 do
            sum = sum + i
        end
        """
        success , message , state = run(code)
        memory_state : dict = state.memory[0]
        self.assertEqual(memory_state.get("sum"), 9)

    def test_loop_reverse_step(self):
        code = """
        sum = 0
        for i = 3, 1, -1 do
            sum = sum + i
        end
        """
        success , message , state = run(code)
        memory_state : dict = state.memory[0]
        self.assertEqual(memory_state.get("sum"), 6)

    def test_loop_single_iteration(self):
        code = """
        for i = 5, 5 do
            x = 10
        end
        """
        success , message , state = run(code)
        memory_state : dict = state.memory[0]
        self.assertEqual(memory_state.get("x"), 10)

    def test_loop_never_runs(self):
        code = """
        for i = 1, 0 do
            x = 5
        end
        """
        success , message , state = run(code)
        memory_state : dict = state.memory[0]
        self.assertIsNone(memory_state.get("x"))

    def test_nested_for_loops(self):
        code = """
        count = 0
        for i = 1, 3 do
            for j = 1, 3 do
                count = count + 1
            end
        end
        """
        success , message , state = run(code)
        memory_state : dict = state.memory[0]
        self.assertEqual(memory_state.get("count"), 9)
