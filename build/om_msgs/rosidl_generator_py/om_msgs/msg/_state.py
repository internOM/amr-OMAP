# generated from rosidl_generator_py/resource/_idl.py.em
# with input from om_msgs:msg/State.idl
# generated code does not contain a copyright notice

# This is being done at the module level and not on the instance level to avoid looking
# for the same variable multiple times on each instance. This variable is not supposed to
# change during runtime so it makes sense to only look for it once.
from os import getenv

ros_python_check_fields = getenv('ROS_PYTHON_CHECK_FIELDS', default='')


# Import statements for member types

import builtins  # noqa: E402, I100

import rosidl_parser.definition  # noqa: E402, I100


class Metaclass_State(type):
    """Metaclass of message 'State'."""

    _CREATE_ROS_MESSAGE = None
    _CONVERT_FROM_PY = None
    _CONVERT_TO_PY = None
    _DESTROY_ROS_MESSAGE = None
    _TYPE_SUPPORT = None

    __constants = {
    }

    @classmethod
    def __import_type_support__(cls):
        try:
            from rosidl_generator_py import import_type_support
            module = import_type_support('om_msgs')
        except ImportError:
            import logging
            import traceback
            logger = logging.getLogger(
                'om_msgs.msg.State')
            logger.debug(
                'Failed to import needed modules for type support:\n' +
                traceback.format_exc())
        else:
            cls._CREATE_ROS_MESSAGE = module.create_ros_message_msg__msg__state
            cls._CONVERT_FROM_PY = module.convert_from_py_msg__msg__state
            cls._CONVERT_TO_PY = module.convert_to_py_msg__msg__state
            cls._TYPE_SUPPORT = module.type_support_msg__msg__state
            cls._DESTROY_ROS_MESSAGE = module.destroy_ros_message_msg__msg__state

    @classmethod
    def __prepare__(cls, name, bases, **kwargs):
        # list constant names here so that they appear in the help text of
        # the message class under "Data and other attributes defined here:"
        # as well as populate each message instance
        return {
        }


class State(metaclass=Metaclass_State):
    """Message class 'State'."""

    __slots__ = [
        '_state_driver',
        '_state_mes',
        '_state_error',
        '_check_fields',
    ]

    _fields_and_field_types = {
        'state_driver': 'int8',
        'state_mes': 'int8',
        'state_error': 'int8',
    }

    # This attribute is used to store an rosidl_parser.definition variable
    # related to the data type of each of the components the message.
    SLOT_TYPES = (
        rosidl_parser.definition.BasicType('int8'),  # noqa: E501
        rosidl_parser.definition.BasicType('int8'),  # noqa: E501
        rosidl_parser.definition.BasicType('int8'),  # noqa: E501
    )

    def __init__(self, **kwargs):
        if 'check_fields' in kwargs:
            self._check_fields = kwargs['check_fields']
        else:
            self._check_fields = ros_python_check_fields == '1'
        if self._check_fields:
            assert all('_' + key in self.__slots__ for key in kwargs.keys()), \
                'Invalid arguments passed to constructor: %s' % \
                ', '.join(sorted(k for k in kwargs.keys() if '_' + k not in self.__slots__))
        self.state_driver = kwargs.get('state_driver', int())
        self.state_mes = kwargs.get('state_mes', int())
        self.state_error = kwargs.get('state_error', int())

    def __repr__(self):
        typename = self.__class__.__module__.split('.')
        typename.pop()
        typename.append(self.__class__.__name__)
        args = []
        for s, t in zip(self.get_fields_and_field_types().keys(), self.SLOT_TYPES):
            field = getattr(self, s)
            fieldstr = repr(field)
            # We use Python array type for fields that can be directly stored
            # in them, and "normal" sequences for everything else.  If it is
            # a type that we store in an array, strip off the 'array' portion.
            if (
                isinstance(t, rosidl_parser.definition.AbstractSequence) and
                isinstance(t.value_type, rosidl_parser.definition.BasicType) and
                t.value_type.typename in ['float', 'double', 'int8', 'uint8', 'int16', 'uint16', 'int32', 'uint32', 'int64', 'uint64']
            ):
                if len(field) == 0:
                    fieldstr = '[]'
                else:
                    if self._check_fields:
                        assert fieldstr.startswith('array(')
                    prefix = "array('X', "
                    suffix = ')'
                    fieldstr = fieldstr[len(prefix):-len(suffix)]
            args.append(s + '=' + fieldstr)
        return '%s(%s)' % ('.'.join(typename), ', '.join(args))

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        if self.state_driver != other.state_driver:
            return False
        if self.state_mes != other.state_mes:
            return False
        if self.state_error != other.state_error:
            return False
        return True

    @classmethod
    def get_fields_and_field_types(cls):
        from copy import copy
        return copy(cls._fields_and_field_types)

    @builtins.property
    def state_driver(self):
        """Message field 'state_driver'."""
        return self._state_driver

    @state_driver.setter
    def state_driver(self, value):
        if self._check_fields:
            assert \
                isinstance(value, int), \
                "The 'state_driver' field must be of type 'int'"
            assert value >= -128 and value < 128, \
                "The 'state_driver' field must be an integer in [-128, 127]"
        self._state_driver = value

    @builtins.property
    def state_mes(self):
        """Message field 'state_mes'."""
        return self._state_mes

    @state_mes.setter
    def state_mes(self, value):
        if self._check_fields:
            assert \
                isinstance(value, int), \
                "The 'state_mes' field must be of type 'int'"
            assert value >= -128 and value < 128, \
                "The 'state_mes' field must be an integer in [-128, 127]"
        self._state_mes = value

    @builtins.property
    def state_error(self):
        """Message field 'state_error'."""
        return self._state_error

    @state_error.setter
    def state_error(self, value):
        if self._check_fields:
            assert \
                isinstance(value, int), \
                "The 'state_error' field must be of type 'int'"
            assert value >= -128 and value < 128, \
                "The 'state_error' field must be an integer in [-128, 127]"
        self._state_error = value
