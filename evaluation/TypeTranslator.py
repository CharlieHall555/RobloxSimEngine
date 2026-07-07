import typing

def type_translation(value : typing.Any) -> str:
    from classes.roblox_classes import class_mappings

    if isinstance(value , float):
        return "number"
    elif isinstance(value , str):
        return "string"
    else:
        return str(type(value))