// generated from rosidl_generator_py/resource/_idl_support.c.em
// with input from om_msgs:msg/State.idl
// generated code does not contain a copyright notice
#define NPY_NO_DEPRECATED_API NPY_1_7_API_VERSION
#include <Python.h>
#include <stdbool.h>
#ifndef _WIN32
# pragma GCC diagnostic push
# pragma GCC diagnostic ignored "-Wunused-function"
#endif
#include "numpy/ndarrayobject.h"
#ifndef _WIN32
# pragma GCC diagnostic pop
#endif
#include "rosidl_runtime_c/visibility_control.h"
#include "om_msgs/msg/detail/state__struct.h"
#include "om_msgs/msg/detail/state__functions.h"


ROSIDL_GENERATOR_C_EXPORT
bool om_msgs__msg__state__convert_from_py(PyObject * _pymsg, void * _ros_message)
{
  // check that the passed message is of the expected Python class
  {
    char full_classname_dest[25];
    {
      char * class_name = NULL;
      char * module_name = NULL;
      {
        PyObject * class_attr = PyObject_GetAttrString(_pymsg, "__class__");
        if (class_attr) {
          PyObject * name_attr = PyObject_GetAttrString(class_attr, "__name__");
          if (name_attr) {
            class_name = (char *)PyUnicode_1BYTE_DATA(name_attr);
            Py_DECREF(name_attr);
          }
          PyObject * module_attr = PyObject_GetAttrString(class_attr, "__module__");
          if (module_attr) {
            module_name = (char *)PyUnicode_1BYTE_DATA(module_attr);
            Py_DECREF(module_attr);
          }
          Py_DECREF(class_attr);
        }
      }
      if (!class_name || !module_name) {
        return false;
      }
      snprintf(full_classname_dest, sizeof(full_classname_dest), "%s.%s", module_name, class_name);
    }
    assert(strncmp("om_msgs.msg._state.State", full_classname_dest, 24) == 0);
  }
  om_msgs__msg__State * ros_message = _ros_message;
  {  // state_driver
    PyObject * field = PyObject_GetAttrString(_pymsg, "state_driver");
    if (!field) {
      return false;
    }
    assert(PyLong_Check(field));
    ros_message->state_driver = (int8_t)PyLong_AsLong(field);
    Py_DECREF(field);
  }
  {  // state_mes
    PyObject * field = PyObject_GetAttrString(_pymsg, "state_mes");
    if (!field) {
      return false;
    }
    assert(PyLong_Check(field));
    ros_message->state_mes = (int8_t)PyLong_AsLong(field);
    Py_DECREF(field);
  }
  {  // state_error
    PyObject * field = PyObject_GetAttrString(_pymsg, "state_error");
    if (!field) {
      return false;
    }
    assert(PyLong_Check(field));
    ros_message->state_error = (int8_t)PyLong_AsLong(field);
    Py_DECREF(field);
  }

  return true;
}

ROSIDL_GENERATOR_C_EXPORT
PyObject * om_msgs__msg__state__convert_to_py(void * raw_ros_message)
{
  /* NOTE(esteve): Call constructor of State */
  PyObject * _pymessage = NULL;
  {
    PyObject * pymessage_module = PyImport_ImportModule("om_msgs.msg._state");
    assert(pymessage_module);
    PyObject * pymessage_class = PyObject_GetAttrString(pymessage_module, "State");
    assert(pymessage_class);
    Py_DECREF(pymessage_module);
    _pymessage = PyObject_CallObject(pymessage_class, NULL);
    Py_DECREF(pymessage_class);
    if (!_pymessage) {
      return NULL;
    }
  }
  om_msgs__msg__State * ros_message = (om_msgs__msg__State *)raw_ros_message;
  {  // state_driver
    PyObject * field = NULL;
    field = PyLong_FromLong(ros_message->state_driver);
    {
      int rc = PyObject_SetAttrString(_pymessage, "state_driver", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }
  {  // state_mes
    PyObject * field = NULL;
    field = PyLong_FromLong(ros_message->state_mes);
    {
      int rc = PyObject_SetAttrString(_pymessage, "state_mes", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }
  {  // state_error
    PyObject * field = NULL;
    field = PyLong_FromLong(ros_message->state_error);
    {
      int rc = PyObject_SetAttrString(_pymessage, "state_error", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }

  // ownership of _pymessage is transferred to the caller
  return _pymessage;
}
