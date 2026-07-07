import unittest
from unittest.mock import patch

from post_evaluation.Objective_Evaluation import (
    eval_expected_output,
    eval_expected_memory,
    eval_expected_function_calls,
)
from post_evaluation.Objective import Objective, FunctionCall
from main import run
