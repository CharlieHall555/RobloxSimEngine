import unittest
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))

from main import run
from syntax_tree.ASTBuilder import ASTBuilder
from syntax_tree.ASTNodes import (
    AssignmentNode, VarNode, NumberNode, OperatorNode, ExpressionNode, UnaryNode
)

class EvalAssignmentTest(unittest.TestCase):

    def test_single_assignment(self):
        code = "x = 20"
        success , message , state = run(code)
        memory_state = state.memory[0]
        self.assertEqual(memory_state.get("x"), 20)

    def test_multiple_assignments(self):
        code = """
        x = 10
        y = 15
        """
        success , message , state = run(code)
        memory_state = state.memory[0]
        self.assertEqual(memory_state.get("x"), 10)
        self.assertEqual(memory_state.get("y"), 15)
        
    def test_reassignment(self):
        code = """
        x = 10
        x = 99
        """
        success , message , state = run(code)
        memory_state = state.memory[0]
        self.assertEqual(memory_state.get("x"), 99)

    def test_assignment_with_addition(self):
        code = """
        x = 5
        y = x + 3
        """
        success , message , state = run(code)
        memory_state = state.memory[0]
        self.assertEqual(memory_state.get("x"), 5)
        self.assertEqual(memory_state.get("y"), 8)

    def test_assignment_with_expression_chain(self):
        code = """
        x = 2
        y = 3
        z = x * y + 5
        """
        success , message , state = run(code)
        memory_state = state.memory[0]
        self.assertEqual(memory_state.get("x"), 2)
        self.assertEqual(memory_state.get("y"), 3)
        self.assertEqual(memory_state.get("z"), 11)

    def test_unary_minus(self):
        code = "x = -10"
        success , message , state = run(code)
        memory_state = state.memory[0]
        self.assertEqual(memory_state.get("x"), -10)

    def test_unary_with_expression(self):
        code = """
        x = 5
        y = -(x + 1)
        """
        success , message , state = run(code)
        memory_state = state.memory[0]
        self.assertEqual(memory_state.get("x"), 5)
        self.assertEqual(memory_state.get("y"), -6)