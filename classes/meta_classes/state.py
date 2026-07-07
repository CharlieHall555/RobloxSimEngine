from __future__ import annotations
import typing


if typing.TYPE_CHECKING:
    from classes.roblox_classes.rbxscriptconnection import RBXScriptConnection
    from classes.meta_classes.datamodel import Datamodel


class State:
    memory : typing.List[typing.Dict[typing.Optional[str], typing.Any]]
    built_in_memory : typing.Dict[typing.Optional[str], typing.Any]
    output : list[str]
    max_run_time : float
    start_time : float
    current_function : list[str]
    return_result : list[typing.Any]
    event_connections : list[RBXScriptConnection]
    datamodel : typing.Optional[Datamodel]
    def __init__(self , datamodel : typing.Optional[Datamodel] , start_memory = [{}] , start_time=0.0 , max_run_time=0.0):
        self.memory = start_memory
        self.start_time = start_time
        self.max_run_time = max_run_time
        self.built_in_memory = {}
        self.current_function = []
        self.return_result = []
        self.output = []
        self.event_connections = []
        self.datamodel = datamodel

    def __str__(self):

        output = " State ".center(16, "-")
        output += "\n"
        output += str(self.memory)
        output += "\n"
        output += " Output ".center(16 , "-")
        output += "\n"
        output += str(self.output)
        output += "\n"
        output += " Connection ".center(16 , "-")
        output += "\n"
        output += str(self.event_connections)
        return output
    