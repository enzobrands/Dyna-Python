from ...common.errors import *
from enum import IntEnum

class ComponentType(IntEnum):
    WHO = 1
    WHAT = 2
    WHERE = 3
    WHEN = 4

    def __str__(self):
        return self.name.title()

    @classmethod
    def from_string(cls, string):
        u_string = string.upper()
        for name, member in cls.__members__.items():
            if name == u_string:
                return member
        raise ComponentError()

