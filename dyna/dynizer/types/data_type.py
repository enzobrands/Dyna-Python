from ...common.errors import *
from enum import IntEnum

class DataType(IntEnum):
    INTEGER = 1
    STRING = 2
    BOOLEAN = 3
    DECIMAL = 4
    TIMESTAMP = 5
    URI = 6
    VOID = 7

    def __str__(self):
        return 'URI' if self == DataType.URI else '{0}'.format(self.name).title()

    @classmethod
    def from_string(cls, string):
        u_string = string.upper()
        for name, member in cls.__members__.items():
            if name == u_string:
                return member
        raise DatatypeError()


