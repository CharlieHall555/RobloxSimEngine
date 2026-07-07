from __future__ import annotations

import typing


if typing.TYPE_CHECKING: from classes.roblox_classes.instance import Instance

class Context:
    data_model : typing.Optional[Instance]
    def __init__(self):
        self.data_model = None