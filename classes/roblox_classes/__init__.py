from classes.roblox_classes.instance import Instance
from classes.roblox_classes.part import Part
from classes.roblox_classes.rbxscriptconnection import RBXScriptConnection
from classes.roblox_classes.rbxscriptsignal import RBXScriptSignal
from classes.roblox_classes.workspace import Workspace

import typing

class_mappings : typing.Dict[str , typing.Callable] = {

    "Workspace" : Workspace,
    "Part" : Part

}
