from ...common.decorators import *
from ...common.errors import *
import json

@valid_field_filters('id', 'name', 'actiontype')
class Action:
    def __init__(self, id=None, name=None, actiontype=None):
        self.id = id
        self.name = name
        self.actiontype = actiontype

    @staticmethod
    def from_dict(dct):
        retval = None
        try:
            if type(dct).__name__ == 'list':
                retval = []
                for d in dct:
                    retval.append(Action.from_dict(d))
            else:
                retval = Action(dct.get('id', None),
                                dct['name'],
                                dct['actiontype'])
        except Exception as e:
            raise DeserializationError(Action, 'dict', dct) from e
        return retval

    @staticmethod
    def from_json(json_string):
        retval = None
        try:
            data = json.loads(json_string)
            retval = Action.from_dict(data)
        except Exception as e:
            raise DeserializationError(Action, 'json', json_string) from e
        return retval

    def to_dict(self):
        dct = None
        try:
            dct = {
                    'name': self.name,
                    'actiontype': self.actiontype
                  }
            if self.id is not None:
                dct['id'] = self.id
        except Exception as e:
            raise SerializationError(Action, 'dict') from e
        return dct

    def to_json(self):
        json_string = ""
        try:
            dct = self.to_dict()
            json_string = json.dumps(dct)
        except Exception as e:
            raise SerializationError(Action, 'json') from e
        return json_string

