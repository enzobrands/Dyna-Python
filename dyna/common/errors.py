class DynaError(Exception):
    """Base class for exceptions in this module."""
    pass



class SerializationError(DynaError):
    """Exception raised for serialization errors.

    Attributes:
        type -- type being serialized
        format -- serialization format
        message -- explanation of the error
    """

    def __init__(self, type, format, message="Serialization Error"):
        self.type = type
        self.format = format
        self.message = '{0}: Type: {1} Format: {2}'.format(message, type.__name__, format)



class DeserializationError(DynaError):
    """Exception raised for deserialization errors.

    Attributes:
        type -- type being deserialized to
        format -- serialized format being deserialized from
        data -- the serialized data
        message -- explanation of the error
    """

    def __init__(self, type, format, data, message="Deserialization Error"):
        self.type = type
        self.format = format
        self.data = data
        self.message = '{0}: Type: {1} Format: {2} Data: {3}'.format(message, type.__name__, format, data)



class ComponentError(DynaError):
    """Exception raised for invalid component types."""
    def __init__(self):
        self.message = "Invalid component type specified"

class DatatypeError(DynaError):
    """Exception raise for invalid datatypes."""
    def __init__(self):
        self.message = "Invalid datatype specified"

class DispatchError(DynaError):
    """Exception raised for an invalid dispatch."""
    def __init__(self, type, operation, message="Dispatch Error"):
        self.type = type
        self.operation = operation
        self.message = '{0}: Type: {1} Operation: {2}'.format(message, type.__name__, operation)

class TranslateError(DynaError):
    """Exception raised for an invalid type translation from string"""
    def __init__(self, type, string, message="Translate Error"):
        self.type = type
        self.string = string
        self.message = '{0}: Type: {1} String: {2}'.format(message, type.__name__, string)

class FilterError(DynaError):
    """Exception raised when an invalid filter is requested"""
    def __init__(self, type, field, message="Filter Error"):
        self.type = type
        self.field = field
        self.message = '{0}: Type: {1} Field: {2}'.format(message, type.__name__, field)

class RequestError(DynaError):
    """Exception raised when an invalid response is returned"""
    def __init__(self, http_status, reason, message="Request Error"):
        self.http_status = http_status
        self.reason = reason
        self.message = '{0}: {1} - {2}'.format(message, http_status, reason)

class ConnectionError(DynaError):
    """Exception raised when the connection to the dynizer failed"""
    def __init__(self, message="Connection Error"):
        self.message = message

class ResponseError(DynaError):
    """Exception raised when the returned result is not as expected"""
    def __init__(self, message="Response Error"):
        self.message = message


