from ...common.errors import *
from ...common.decorators import *
from enum import Enum

class FilterOperator(Enum):
    EQ = 1
    LT = 2
    LTEQ = 3
    GT = 4
    GTEQ = 5
    NEQ = 6
    TSRCH = 7

    @staticmethod
    @static_func_vars(trmap={
        1: '=',
        2: '<',
        3: '<=',
        4: '>',
        5: '>=',
        6: '!=',
        7: '~='
    })
    def __to_str(v):
        return FilterOperator.__to_str.trmap[int(v)]

    def __str__(self):
        return FilterOperator.__to_str(self.value)

    def to_url_operator(self):
        if self.value == FilterOperator.EQ.value:
            return ''
        else:
            return FilterOperator.__to_str(self.value)

    @classmethod
    @static_func_vars(trmap={
        '=': 'EQ',
        '<': 'LT',
        '<=': 'LTEQ',
        '>': 'GT',
        '>=': 'GTEQ',
        '!=': 'NEQ',
        '~=': 'TSRCH'
    })
    def from_string(cls, string):
        op_name = FilterOperators.from_string.trmap[string]
        for name, member in cls.__member__.items():
            if name == op_name:
                return member
        raise TranslateError(FilterOperators, string)

