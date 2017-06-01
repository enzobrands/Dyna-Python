from dyna.dynizer.connector import *
from dyna.dynizer.types import *

def test_Certificates():
    conn = DynizerConnector("api.unittest.dynizer.com",
                            https=True,
                            key_file="tests/resources/unittest.key",
                            cert_file="tests/resources/unittest.crt")
    conn.connect()
    res = conn.read(Action())
    assert(type(res) == list)
    assert(len(res) > 0)
    assert(type(res[0]) == Action)

    conn.close()

