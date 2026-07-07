import time
from classes.meta_classes.state import State
import re
from antlr4 import *
from parser.LuaLexer import LuaLexer
from parser.LuaParser import LuaParser
from syntax_tree.ASTBuilder import ASTBuilder
from syntax_tree.ASTNodes import ASTNode
import typing
import evaluation.EvaluationEngine as eval
from evaluation.BuiltInState import setup_state
from post_evaluation.Objective import Objective
from evaluation.DataModelGenerator import generate_data_model , default_data_model

from classes.meta_classes.datamodel import Datamodel

test_objective = Objective(["hello-world"] , {"y" : 7})

def __init__():
    pass


def preprocess_lua_code(code):
    compound_ops = {
        r'\+=': '+',
        r'-=': '-',
        r'\*=': '*',
        r'/=': '/',
    }

    for pattern, op in compound_ops.items():
        regex = re.compile(rf'(\b\w+\b)\s*{pattern}\s*(.+)')
        code = regex.sub(rf'\1 = \1 {op} \2', code)

    return code


def display_result(state: State, ast: ASTNode, duration: float) -> None:
    print("\n[AST Representation]")
    print("-" * 20)
    print(ast)

    print("\n[Evaluation Output]")
    print("-" * 20)
    print(state)

    print("\n[Execution Time]")
    print("-" * 20)
    print(f"{duration:.6f} seconds")


def run(code , datamodel_dict : typing.Optional[dict] = None , print_result=False, max_run_time: float = 0.1) -> typing.Tuple[bool , str, State]:
    start = time.perf_counter()
    status_message = "failed"
    
    datamodel : typing.Optional["Datamodel"] = None

    try: 
        datamodel = generate_data_model(datamodel_dict or default_data_model)
    except:
        print("failed to generate datamodel")
        status_message = "failed to generate datamodel"
        return False , status_message , State(None)

    try:
        processed_code = preprocess_lua_code(code)
        input_stream = InputStream(processed_code)
        lexer = LuaLexer(input_stream)
        token_stream = CommonTokenStream(lexer)
        parser = LuaParser(token_stream)
        parse_tree = parser.start_()
    except:
        print("failed to parse")
        status_message = "failed_to_parse"
        return False , status_message , State(datamodel)

    try:
        builder = ASTBuilder(max_visits=1000)
        ast = builder.visit(parse_tree)
    except:
        print("failed to build")
        status_message = "failed_to_build_ast"
        return False , status_message , State(datamodel)


    starting_state: list[dict] = [{}]

    state: State = State(datamodel=datamodel,
                        start_memory=starting_state,
                         start_time=time.perf_counter(),
                         max_run_time=max_run_time)

    setup_state(state)

    end: float = 0
    duration: float = 0

    #--- Runtime-Phase ---


    try:
        eval.eval(state , ast)
        status_message = "done"
    except SyntaxError:
        print("Syntax error failed to build to AST.")
        status_message = "failed_syntax"
    except RuntimeError:
        print("Runtime error while executing.")
        status_message = "failed_runtime"
    except TimeoutError:
        print("Given too load exceeded given execute time.")
        status_message = "failed_timeout"
    except Exception as e:
        print(f"Generic error : {e}")
        status_message = "failed_generic"
    finally:
        end = time.perf_counter()
        duration = end - start

    if print_result:
        display_result(state, ast, duration)

    if status_message == "done":
        return True , status_message , state
    else:
        return False , status_message , state


lua_code = """
x = Instance.new("Part")
x.Parent = game.Workspace

print(#game.Workspace:GetChildren() , "hello")

print(game.Workspace.Part1.Position)

"""
starting_state = {
  "ClassName": "DataModel",
  "Children": [
    {
      "ClassName": "Workspace",
      "Children": [
        {
          "ClassName": "Part",
          "Properties": {"Name" : "Part1"}
        },
        {
          "ClassName": "Model",
          "Children": [
            {
              "ClassName": "Part"
            }
          ]
        }
      ]
    },
  ]
}

if __name__ == "__main__":
    run(lua_code, starting_state , print_result=True, max_run_time=2)
