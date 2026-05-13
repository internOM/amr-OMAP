// generated from rosidl_generator_py/resource/_idl_support.c.em
// with input from om_msgs:msg/Query.idl
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
#include "om_msgs/msg/detail/query__struct.h"
#include "om_msgs/msg/detail/query__functions.h"

#include "rosidl_runtime_c/primitives_sequence.h"
#include "rosidl_runtime_c/primitives_sequence_functions.h"


ROSIDL_GENERATOR_C_EXPORT
bool om_msgs__msg__query__convert_from_py(PyObject * _pymsg, void * _ros_message)
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
    assert(strncmp("om_msgs.msg._query.Query", full_classname_dest, 24) == 0);
  }
  om_msgs__msg__Query * ros_message = _ros_message;
  {  // slave_id
    PyObject * field = PyObject_GetAttrString(_pymsg, "slave_id");
    if (!field) {
      return false;
    }
    assert(PyLong_Check(field));
    ros_message->slave_id = (int8_t)PyLong_AsLong(field);
    Py_DECREF(field);
  }
  {  // func_code
    PyObject * field = PyObject_GetAttrString(_pymsg, "func_code");
    if (!field) {
      return false;
    }
    assert(PyLong_Check(field));
    ros_message->func_code = (int8_t)PyLong_AsLong(field);
    Py_DECREF(field);
  }
  {  // write_addr
    PyObject * field = PyObject_GetAttrString(_pymsg, "write_addr");
    if (!field) {
      return false;
    }
    assert(PyLong_Check(field));
    ros_message->write_addr = (int32_t)PyLong_AsLong(field);
    Py_DECREF(field);
  }
  {  // read_addr
    PyObject * field = PyObject_GetAttrString(_pymsg, "read_addr");
    if (!field) {
      return false;
    }
    assert(PyLong_Check(field));
    ros_message->read_addr = (int32_t)PyLong_AsLong(field);
    Py_DECREF(field);
  }
  {  // write_num
    PyObject * field = PyObject_GetAttrString(_pymsg, "write_num");
    if (!field) {
      return false;
    }
    assert(PyLong_Check(field));
    ros_message->write_num = (int8_t)PyLong_AsLong(field);
    Py_DECREF(field);
  }
  {  // read_num
    PyObject * field = PyObject_GetAttrString(_pymsg, "read_num");
    if (!field) {
      return false;
    }
    assert(PyLong_Check(field));
    ros_message->read_num = (int8_t)PyLong_AsLong(field);
    Py_DECREF(field);
  }
  {  // data
    PyObject * field = PyObject_GetAttrString(_pymsg, "data");
    if (!field) {
      return false;
    }
    {
      // TODO(dirk-thomas) use a better way to check the type before casting
      assert(field->ob_type != NULL);
      assert(field->ob_type->tp_name != NULL);
      assert(strcmp(field->ob_type->tp_name, "numpy.ndarray") == 0);
      PyArrayObject * seq_field = (PyArrayObject *)field;
      Py_INCREF(seq_field);
      assert(PyArray_NDIM(seq_field) == 1);
      assert(PyArray_TYPE(seq_field) == NPY_INT32);
      Py_ssize_t size = 64;
      int32_t * dest = ros_message->data;
      for (Py_ssize_t i = 0; i < size; ++i) {
        int32_t tmp = *(npy_int32 *)PyArray_GETPTR1(seq_field, i);
        memcpy(&dest[i], &tmp, sizeof(int32_t));
      }
      Py_DECREF(seq_field);
    }
    Py_DECREF(field);
  }

  return true;
}

ROSIDL_GENERATOR_C_EXPORT
PyObject * om_msgs__msg__query__convert_to_py(void * raw_ros_message)
{
  /* NOTE(esteve): Call constructor of Query */
  PyObject * _pymessage = NULL;
  {
    PyObject * pymessage_module = PyImport_ImportModule("om_msgs.msg._query");
    assert(pymessage_module);
    PyObject * pymessage_class = PyObject_GetAttrString(pymessage_module, "Query");
    assert(pymessage_class);
    Py_DECREF(pymessage_module);
    _pymessage = PyObject_CallObject(pymessage_class, NULL);
    Py_DECREF(pymessage_class);
    if (!_pymessage) {
      return NULL;
    }
  }
  om_msgs__msg__Query * ros_message = (om_msgs__msg__Query *)raw_ros_message;
  {  // slave_id
    PyObject * field = NULL;
    field = PyLong_FromLong(ros_message->slave_id);
    {
      int rc = PyObject_SetAttrString(_pymessage, "slave_id", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }
  {  // func_code
    PyObject * field = NULL;
    field = PyLong_FromLong(ros_message->func_code);
    {
      int rc = PyObject_SetAttrString(_pymessage, "func_code", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }
  {  // write_addr
    PyObject * field = NULL;
    field = PyLong_FromLong(ros_message->write_addr);
    {
      int rc = PyObject_SetAttrString(_pymessage, "write_addr", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }
  {  // read_addr
    PyObject * field = NULL;
    field = PyLong_FromLong(ros_message->read_addr);
    {
      int rc = PyObject_SetAttrString(_pymessage, "read_addr", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }
  {  // write_num
    PyObject * field = NULL;
    field = PyLong_FromLong(ros_message->write_num);
    {
      int rc = PyObject_SetAttrString(_pymessage, "write_num", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }
  {  // read_num
    PyObject * field = NULL;
    field = PyLong_FromLong(ros_message->read_num);
    {
      int rc = PyObject_SetAttrString(_pymessage, "read_num", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }
  {  // data
    PyObject * field = NULL;
    field = PyObject_GetAttrString(_pymessage, "data");
    if (!field) {
      return NULL;
    }
    assert(field->ob_type != NULL);
    assert(field->ob_type->tp_name != NULL);
    assert(strcmp(field->ob_type->tp_name, "numpy.ndarray") == 0);
    PyArrayObject * seq_field = (PyArrayObject *)field;
    assert(PyArray_NDIM(seq_field) == 1);
    assert(PyArray_TYPE(seq_field) == NPY_INT32);
    assert(sizeof(npy_int32) == sizeof(int32_t));
    npy_int32 * dst = (npy_int32 *)PyArray_GETPTR1(seq_field, 0);
    int32_t * src = &(ros_message->data[0]);
    memcpy(dst, src, 64 * sizeof(int32_t));
    Py_DECREF(field);
  }

  // ownership of _pymessage is transferred to the caller
  return _pymessage;
}
