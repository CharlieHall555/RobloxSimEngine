from __future__ import annotations

import typing
from evaluation.TypeTranslator import type_translation

if typing.TYPE_CHECKING:
    from classes.meta_classes.state import State

def raise_error(state : State , error_message : str):
    state.output.append(error_message)
    raise RuntimeError(error_message)

def raise_add_type_error(state: State, val1: typing.Any, val2: typing.Any):
    t1 = type_translation(val1)
    t2 = type_translation(val2)
    raise_error(state, f"attempt to perform arithmetic (add) on {t1} and {t2}")

def raise_sub_type_error(state: State, val1: typing.Any, val2: typing.Any):
    t1 = type_translation(val1)
    t2 = type_translation(val2)
    raise_error(state, f"attempt to perform arithmetic (sub) on {t1} and {t2}")

def raise_mul_type_error(state: State, val1: typing.Any, val2: typing.Any):
    t1 = type_translation(val1)
    t2 = type_translation(val2)
    raise_error(state, f"attempt to perform arithmetic (mul) on {t1} and {t2}")

def raise_div_type_error(state: State, val1: typing.Any, val2: typing.Any):
    t1 = type_translation(val1)
    t2 = type_translation(val2)
    raise_error(state, f"attempt to perform arithmetic (div) on {t1} and {t2}")

def raise_idiv_type_error(state: State, val1: typing.Any, val2: typing.Any):
    t1 = type_translation(val1)
    t2 = type_translation(val2)
    raise_error(state, f"attempt to perform arithmetic (idiv) on {t1} and {t2}")

def raise_mod_type_error(state: State, val1: typing.Any, val2: typing.Any):
    t1 = type_translation(val1)
    t2 = type_translation(val2)
    raise_error(state, f"attempt to perform arithmetic (mod) on {t1} and {t2}")

def raise_pow_type_error(state: State, val1: typing.Any, val2: typing.Any):
    t1 = type_translation(val1)
    t2 = type_translation(val2)
    raise_error(state, f"attempt to perform arithmetic (pow) on {t1} and {t2}")

def raise_unm_type_error(state: State, val: typing.Any):
    t = type_translation(val)
    raise_error(state, f"attempt to perform arithmetic (unm) on {t}")

def raise_concat_type_error(state: State, val1: typing.Any, val2: typing.Any):
    t1 = type_translation(val1)
    t2 = type_translation(val2)
    raise_error(state, f"attempt to concatenate {t1} and {t2}")

def raise_len_type_error(state: State, val: typing.Any):
    t = type_translation(val)
    raise_error(state, f"attempt to get length of a {t}")

def raise_eq_type_error(state: State, val1: typing.Any, val2: typing.Any):
    t1 = type_translation(val1)
    t2 = type_translation(val2)
    raise_error(state, f"attempt to compare {t1} with {t2}")