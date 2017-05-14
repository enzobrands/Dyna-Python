from dyna.dynizer.types import *
from dyna.common.errors import *
import pytest

def test_ComponentType():
    assert(str(ComponentType.WHERE) == 'Where')
    assert(ComponentType.from_string('when') == ComponentType.WHEN)
    with pytest.raises(ComponentError):
        ComponentType.from_string('how')

def test_DataType():
    assert(str(DataType.STRING) == 'String')
    assert(str(DataType.URI) == 'URI')
    assert(DataType.from_string('timestamp') == DataType.TIMESTAMP)
    with pytest.raises(DatatypeError):
        DataType.from_string('float')



