import enum


class HRESULT(enum.IntEnum):
    UNKNOWN_ERROR = 0xFFFFFFFF
    WBEM_E_FAILED = 0x80041001
    WBEM_E_NOT_FOUND = 0x80041002
    WBEM_E_ACCESS_DENIED = 0x80041003
    WBEM_E_PROVIDER_FAILURE = 0x80041004
    WBEM_E_TYPE_MISMATCH = 0x80041005
    WBEM_E_OUT_OF_MEMORY = 0x80041006
    WBEM_E_INVALID_CONTEXT = 0x80041007
    WBEM_E_INVALID_PARAMETER = 0x80041008
    WBEM_E_NOT_AVAILABLE = 0x80041009
    WBEM_E_CRITICAL_ERROR = 0x8004100A
    WBEM_E_INVALID_STREAM = 0x8004100B
    WBEM_E_NOT_SUPPORTED = 0x8004100C
    WBEM_E_INVALID_SUPERCLASS = 0x8004100D
    WBEM_E_INVALID_NAMESPACE = 0x8004100E
    WBEM_E_INVALID_OBJECT = 0x8004100F
    WBEM_E_INVALID_CLASS = 0x80041010
    WBEM_E_PROVIDER_NOT_FOUND = 0x80041011
    WBEM_E_INVALID_PROVIDER_REGISTRATION = 0x80041012
    WBEM_E_PROVIDER_LOAD_FAILURE = 0x80041013
    WBEM_E_INITIALIZATION_FAILURE = 0x80041014
    WBEM_E_TRANSPORT_FAILURE = 0x80041015
    WBEM_E_INVALID_OPERATION = 0x80041016
    WBEM_E_INVALID_QUERY = 0x80041017
    WBEM_E_INVALID_QUERY_TYPE = 0x80041018
    WBEM_E_ALREADY_EXISTS = 0x80041019
    WBEM_E_OVERRIDE_NOT_ALLOWED = 0x8004101A
    WBEM_E_PROPAGATED_QUALIFIER = 0x8004101B
    WBEM_E_PROPAGATED_PROPERTY = 0x8004101C
    WBEM_E_UNEXPECTED = 0x8004101D
    WBEM_E_ILLEGAL_OPERATION = 0x8004101E
    WBEM_E_CANNOT_BE_KEY = 0x8004101F

    def describe(self) -> str:
        """返回 HRESULT 的描述字符串"""
        return {
            HRESULT.UNKNOWN_ERROR: 'Unknown Error',
            HRESULT.WBEM_E_FAILED: 'Call failed',
            HRESULT.WBEM_E_NOT_FOUND: 'Object cannot be found',
            HRESULT.WBEM_E_ACCESS_DENIED: 'Current user does not have permission to perform the action',
            HRESULT.WBEM_E_PROVIDER_FAILURE: 'Provider has failed at some time other than during initialization',
            HRESULT.WBEM_E_TYPE_MISMATCH: 'Type mismatch occurred',
            HRESULT.WBEM_E_OUT_OF_MEMORY: 'Not enough memory for the operation',
            HRESULT.WBEM_E_INVALID_CONTEXT: 'The IWbemContext object is not valid',
            HRESULT.WBEM_E_INVALID_PARAMETER: 'One of the parameters to the call is not correct',
            HRESULT.WBEM_E_NOT_AVAILABLE: 'Resource, typically a remote server, is not currently available.',
            HRESULT.WBEM_E_CRITICAL_ERROR: 'Internal, critical, and unexpected error occurred. Report the error to Microsoft Technical Support.',
            HRESULT.WBEM_E_INVALID_STREAM: 'One or more network packets were corrupted during a remote session',
            HRESULT.WBEM_E_NOT_SUPPORTED: 'Feature or operation is not supported',
            HRESULT.WBEM_E_INVALID_SUPERCLASS: 'Parent class specified is not valid',
            HRESULT.WBEM_E_INVALID_NAMESPACE: 'Namespace specified cannot be found.',
            HRESULT.WBEM_E_INVALID_OBJECT: 'Specified instance is not valid',
            HRESULT.WBEM_E_INVALID_CLASS: 'Specified class is not valid.',
            HRESULT.WBEM_E_PROVIDER_NOT_FOUND: 'Provider referenced in the schema does not have a corresponding registration',
            HRESULT.WBEM_E_INVALID_PROVIDER_REGISTRATION: 'Provider referenced in the schema has an incorrect or incomplete registration',
            HRESULT.WBEM_E_PROVIDER_LOAD_FAILURE: 'COM cannot locate a provider referenced in the schema',
            HRESULT.WBEM_E_INITIALIZATION_FAILURE: 'Component, such as a provider, failed to initialize for internal reasons.',
            HRESULT.WBEM_E_TRANSPORT_FAILURE: 'Networking error that prevents normal operation has occurred.',
            HRESULT.WBEM_E_INVALID_OPERATION: 'Requested operation is not valid. This error usually applies to invalid attempts to delete classes or properties.',
            HRESULT.WBEM_E_INVALID_QUERY: 'Query was not syntactically valid',
            HRESULT.WBEM_E_INVALID_QUERY_TYPE: 'Requested query language is not supported',
            HRESULT.WBEM_E_ALREADY_EXISTS: 'In a put operation, the wbemChangeFlagCreateOnly flag was specified, but the instance already exists.',
            HRESULT.WBEM_E_OVERRIDE_NOT_ALLOWED: 'Not possible to perform the add operation on this qualifier because the owning object does not permit overrides.',
            HRESULT.WBEM_E_PROPAGATED_QUALIFIER: 'User attempted to delete a qualifier that was not owned. The qualifier was inherited from a parent class.',
            HRESULT.WBEM_E_PROPAGATED_PROPERTY: 'User attempted to delete a property that was not owned. The property was inherited from a parent class.',
            HRESULT.WBEM_E_UNEXPECTED: 'Client made an unexpected and illegal sequence of calls, such as calling EndEnumeration before calling BeginEnumeration.',
            HRESULT.WBEM_E_ILLEGAL_OPERATION: 'User requested an illegal operation, such as spawning a class from an instance.',
            HRESULT.WBEM_E_CANNOT_BE_KEY: 'Illegal attempt to specify a key qualifier on a property that cannot be a key. The keys are specified in the class definition for an object and cannot be altered on a per-instance basis.',
        }.get(self, f'Unknown HRESULT code: {self.value}')

    def hex(self):
        return hex(self.value)

    @classmethod
    def from_code(cls, code: int) -> "HRESULT":
        try:
            return cls(code & 0xFFFFFFFF)  # 转为无符号 32 位整数
        except ValueError:
            print(f'[!] Invalid HRESULT code: {code} ({code & 0xFFFFFFFF}, hex: {hex(code & 0xFFFFFFFF)})')
            return cls.UNKNOWN_ERROR
