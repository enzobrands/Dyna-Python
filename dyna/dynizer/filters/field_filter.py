from ..types import *
from ...common.errors import *
from .filter import Filter
import urllib

class FieldFilter(Filter):
    def __init__(self, field, op, value):
        self.field = field
        self.op = op
        self.value = value

    def compose_filter(self, cls):
        FieldFilter.__validate_field(cls, self.field)
        # Exception for components filter on Topology class
        if cls.__name__ == Topology.__name__ and self.field == 'components':
            return "{0}={1}'{2}'".format(self.field, self.op.to_url_operator(), self.value)
        else:
            return '{0}={1}{2}'.format(self.field, self.op.to_url_operator(), urllib.parse.quote(self.value))

    @staticmethod
    def __validate_field(cls, field):
        if not cls._can_filter_on(field):
            raise FilterError(cls, field)


