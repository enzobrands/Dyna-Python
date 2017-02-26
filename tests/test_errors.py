from common.errors import *

def test_SerializationError():
    e = SerializationError(str, 'json')
    assert(e.type.__name__ == str.__name__)
    assert(e.format == 'json')
    assert(e.message == 'Serialization Error: Type: {0} Format: json'.format(str.__name__))

def test_DeserializationError():
    e = DeserializationError(str, 'dict', {'a':1, 'b':2})
    assert(e.type.__name__ == str.__name__)
    assert(e.format == 'dict')
    assert(e.data == {'a':1, 'b':2})
    assert(e.message == 'Deserialization Error: Type: {0} Format: dict Data: {1}'.format(str.__name__, {'a':1, 'b':2}))

def test_ComponentError():
    e = ComponentError()
    assert(e.message == 'Invalid component type specified')

def test_DatatypeError():
    e = DatatypeError()
    assert(e.message == 'Invalid datatype specified')

def test_DispatchError():
    e = DispatchError(str, 'fetch')
    assert(e.type.__name__ == str.__name__)
    assert(e.operation == 'fetch')
    assert(e.message == 'Dispatch Error: Type: {0} Operation: fetch'.format(str.__name__))

def test_TranslateError():
    e = TranslateError(str, 'Who')
    assert(e.type.__name__ == str.__name__)
    assert(e.string == 'Who')
    assert(e.message == 'Translate Error: Type: {0} String: Who'.format(str.__name__))

def test_FilterError():
    e = FilterError(str, 'field')
    assert(e.type.__name__ == str.__name__)
    assert(e.field == 'field')
    assert(e.message == 'Filter Error: Type: {0} Field: field'.format(str.__name__))

def test_RequestError():
    e = RequestError(500, 'Internal Server Error')
    assert(e.http_status == 500)
    assert(e.reason == 'Internal Server Error')
    assert(e.message == 'Request Error: 500 - Internal Server Error')

def test_ConnectionError():
    e = ConnectionError()
    assert(e.message == 'Connection Error')

def test_ResponseError():
    e = ResponseError()
    assert(e.message == 'Response Error')
