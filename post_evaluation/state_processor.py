from classes.lua_classes import LuaNumber

def process_memory(memory : list[dict]) -> list:
    output = []
    for stack_frame in memory:
        o_dict = {}
        for key , value in stack_frame.items():

            if isinstance(value , LuaNumber):
                o_dict[key] = value.to_number()
            elif isinstance(value , str) or isinstance(value , float) or isinstance(value , int):
                o_dict[key] = value
            else:
                o_dict[key] = str(value)

        output.append(o_dict)
    return output