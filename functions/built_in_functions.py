from __future__ import annotations

import typing

from classes.meta_classes.state import State

def built_in_print(state: State, *args):
    try:
        line = ""
        for value in args:
            str_value = str(value)
            line += str_value + ", "
        state.output.append(line[:-2])
    except Exception as e:
        raise RuntimeError(f"Error in printing: {e}")
    