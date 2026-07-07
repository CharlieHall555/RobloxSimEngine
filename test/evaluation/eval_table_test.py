import unittest
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))

from main import run
from syntax_tree.ASTBuilder import ASTBuilder
from syntax_tree.ASTNodes import (
    AssignmentNode, VarNode, NumberNode, OperatorNode, ExpressionNode, UnaryNode
)

class EvalTableTest(unittest.TestCase):
    
    def test_create_table(self):
        code = """
        x = {1 , 2 , 3}
        """
        success , message , state = run(code)
        memory_state : dict = state.memory[0]
        self.assertEqual(str(memory_state.get("x")), '{1: LuaNumber(1), 2: LuaNumber(2), 3: LuaNumber(3)}')

    def test_index_table(self):
        code = """
        x = {1 , 2 , 3}
        """
        success , message , state = run(code)
        memory_state : dict = state.memory[0]
        self.assertEqual(str(memory_state.get("x")), '{1: LuaNumber(1), 2: LuaNumber(2), 3: LuaNumber(3)}')

    def test_edit_table(self):
        code = """
        x = {1 , 2 , 3 , 5}
        y = x[4]
        """
        success , message , state = run(code)
        memory_state : dict = state.memory[0]
        self.assertEqual(memory_state.get("y"), 5)

    def test_length_operator_on_string(self):
        code = """
        x = #"hello"
        """
        success , message , state = run(code)
        memory_state : dict = state.memory[0]
        self.assertTrue(success)
        self.assertEqual(memory_state.get("x"), 5)

    def test_length_operator_on_get_children(self):
        code = """
        x = Instance.new("Part")
        y = #x:GetChildren()
        """
        success , message , state = run(code)
        memory_state : dict = state.memory[0]
        self.assertTrue(success)
        self.assertEqual(memory_state.get("y"), 0)
