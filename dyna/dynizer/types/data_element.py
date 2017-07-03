from ...common.decorators import *
from ...common.errors import *
from .data_type import DataType
from decimal import *
import json
import dateutil.parser

@valid_field_filters('id', 'value', 'datatype')
class DataElement:
    def __init__(self, id=None, value=None, datatype=None):
        self.id = id
        self.value = DataElement._format_input_value(datatype, value)
        self.datatype = DataType.VOID if datatype is None else datatype


    @staticmethod
    def _format_input_value(datatype, value):
        if datatype == DataType.INTEGER:
            return int(value)
        if datatype == DataType.STRING:
            return str(value)
        if datatype == DataType.BOOLEAN:
            return bool(value)
        if datatype == DataType.DECIMAL:
            return Decimal(value)
        if datatype == DataType.TIMESTAMP:
            if type(value).__name__ == 'str':
                return dateutil.parser.parse(value)
            if type(value).__name__ == 'date' :
                return datetime.datetime(value.year, value.month, value.day)
            if type(value).__name__ == 'time':
                td = datetime.today()
                return datetime.datetime(td.year, td.month, td.day, value.hour, value.minute, value.second, value.microsecond)
            if type(value).__name__ == 'datetime':
                #return value
                # Remove timezone for now since not supported
                return value.replace(tzinfo=None)
            return datetime.min
        if datatype == DataType.URI:
            return str(value)
        return None


    @staticmethod
    def _convertfrom_json(datatype, value):
        if datatype == DataType.INTEGER:
            return int(value)
        if datatype == DataType.STRING:
            return str(value)
        if datatype == DataType.BOOLEAN:
            return value
        if datatype == DataType.DECIMAL:
            return Decimal(value)
        if datatype == DataType.TIMESTAMP:
            return dateutil.parser.parse(value)
        if datatype == DataType.URI:
            return str(value)
        return None

    @staticmethod
    def _convert_to_json(datatype, value):
        if datatype == DataType.INTEGER:
            return int(value)
        if datatype == DataType.STRING:
            return str(value)
        if datatype == DataType.BOOLEAN:
            return 'true' if value else 'false'
        if datatype == DataType.DECIMAL:
            return str(value)
        if datatype == DataType.TIMESTAMP:
            return str(value.isoformat())
        if datatype == DataType.URI:
            return str(value)
        return 'Void'

    @staticmethod
    def from_dict(dct):
        retval = None
        try:
            if type(dct).__name__ == 'list':
                retval = []
                for d in dct:
                    retval.append(DataElement.from_dict(d))
            else:
                retval = DataElement(dct.get('id', None),
                                     DataElement._convertfrom_json(DataType.from_string(dct['datatype']), dct['value']),
                                     DataType.from_string(dct['datatype']))
        except Exception as e:
            raise DeserializationError(DataElement, 'dict', dct) from e
        return retval

    @staticmethod
    def from_json(json_string):
        retval = None
        try:
            data = json.loads(json_string)
            retval = DataElement.from_dict(data)
        except Exception as e:
            raise DeserializationError(DataElement, 'json', json_string) from e
        return retval


    def to_dict(self):
        dct = None
        try:
            dct = {
                    'value': DataElement._convert_to_json(self.datatype, self.value),
                    'datatype': str(self.datatype)
                  }
            if self.id is not None:
                dct['id'] = self.id
        except Exception as e:
            raise SerializationError(DataElement, 'dict') from e
        return dct

    def to_json(self):
        json_String = ""
        try:
            dct = self.to_dict()
            json_string = json.dumps(dct)
        except Exception as e:
            raise SerializationError(DataElement, 'json') from e
        return json_string


