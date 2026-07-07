import unittest
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))

from main import run
from syntax_tree.ASTBuilder import ASTBuilder
from syntax_tree.ASTNodes import (
    AssignmentNode, VarNode, NumberNode, OperatorNode, ExpressionNode, UnaryNode
)

class EvalRepeatUntilLoopTest(unittest.TestCase):

    def test_repeat_runs_once(self):
        code = """
        x = 0
        repeat
            x = x + 1
        until true
        """
        success , message , state = run(code)
        memory_state : dict = state.memory[0]
        self.assertEqual(memory_state.get("x"), 1)

    def test_repeat_until_false_then_true(self):
        code = """
        x = 0
        repeat
            x = x + 1
        until x == 3
        """
        success , message , state = run(code)
        memory_state : dict = state.memory[0]
        self.assertEqual(memory_state.get("x"), 3)

    def test_nested_repeat_loops(self):
        code = """
        i = 0
        count = 0
        repeat
            i = i + 1
            j = 0
            repeat
                j = j + 1
                count = count + 1
            until j == 3
        until i == 3
        """
        success , message , state = run(code)
        memory_state : dict = state.memory[0]
        self.assertEqual(memory_state.get("i"), 3)
        self.assertEqual(memory_state.get("j"), 3)
        self.assertEqual(memory_state.get("count"), 9)

    def test_repeat_with_expression_condition(self):
        code = """
        x = 0
        repeat
            x = x + 1
        until x >= 5
        """
        success , message , state = run(code)
        memory_state : dict = state.memory[0]
        self.assertEqual(memory_state.get("x"), 5)
