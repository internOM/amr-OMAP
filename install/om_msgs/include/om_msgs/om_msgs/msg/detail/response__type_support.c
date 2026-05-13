// generated from rosidl_typesupport_introspection_c/resource/idl__type_support.c.em
// with input from om_msgs:msg/Response.idl
// generated code does not contain a copyright notice

#include <stddef.h>
#include "om_msgs/msg/detail/response__rosidl_typesupport_introspection_c.h"
#include "om_msgs/msg/rosidl_typesupport_introspection_c__visibility_control.h"
#include "rosidl_typesupport_introspection_c/field_types.h"
#include "rosidl_typesupport_introspection_c/identifier.h"
#include "rosidl_typesupport_introspection_c/message_introspection.h"
#include "om_msgs/msg/detail/response__functions.h"
#include "om_msgs/msg/detail/response__struct.h"


#ifdef __cplusplus
extern "C"
{
#endif

void om_msgs__msg__Response__rosidl_typesupport_introspection_c__Response_init_function(
  void * message_memory, enum rosidl_runtime_c__message_initialization _init)
{
  // TODO(karsten1987): initializers are not yet implemented for typesupport c
  // see https://github.com/ros2/ros2/issues/397
  (void) _init;
  om_msgs__msg__Response__init(message_memory);
}

void om_msgs__msg__Response__rosidl_typesupport_introspection_c__Response_fini_function(void * message_memory)
{
  om_msgs__msg__Response__fini(message_memory);
}

size_t om_msgs__msg__Response__rosidl_typesupport_introspection_c__size_function__Response__data(
  const void * untyped_member)
{
  (void)untyped_member;
  return 64;
}

const void * om_msgs__msg__Response__rosidl_typesupport_introspection_c__get_const_function__Response__data(
  const void * untyped_member, size_t index)
{
  const int32_t * member =
    (const int32_t *)(untyped_member);
  return &member[index];
}

void * om_msgs__msg__Response__rosidl_typesupport_introspection_c__get_function__Response__data(
  void * untyped_member, size_t index)
{
  int32_t * member =
    (int32_t *)(untyped_member);
  return &member[index];
}

void om_msgs__msg__Response__rosidl_typesupport_introspection_c__fetch_function__Response__data(
  const void * untyped_member, size_t index, void * untyped_value)
{
  const int32_t * item =
    ((const int32_t *)
    om_msgs__msg__Response__rosidl_typesupport_introspection_c__get_const_function__Response__data(untyped_member, index));
  int32_t * value =
    (int32_t *)(untyped_value);
  *value = *item;
}

void om_msgs__msg__Response__rosidl_typesupport_introspection_c__assign_function__Response__data(
  void * untyped_member, size_t index, const void * untyped_value)
{
  int32_t * item =
    ((int32_t *)
    om_msgs__msg__Response__rosidl_typesupport_introspection_c__get_function__Response__data(untyped_member, index));
  const int32_t * value =
    (const int32_t *)(untyped_value);
  *item = *value;
}

static rosidl_typesupport_introspection_c__MessageMember om_msgs__msg__Response__rosidl_typesupport_introspection_c__Response_message_member_array[3] = {
  {
    "data",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_INT32,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    false,  // is key
    true,  // is array
    64,  // array size
    false,  // is upper bound
    offsetof(om_msgs__msg__Response, data),  // bytes offset in struct
    NULL,  // default value
    om_msgs__msg__Response__rosidl_typesupport_introspection_c__size_function__Response__data,  // size() function pointer
    om_msgs__msg__Response__rosidl_typesupport_introspection_c__get_const_function__Response__data,  // get_const(index) function pointer
    om_msgs__msg__Response__rosidl_typesupport_introspection_c__get_function__Response__data,  // get(index) function pointer
    om_msgs__msg__Response__rosidl_typesupport_introspection_c__fetch_function__Response__data,  // fetch(index, &value) function pointer
    om_msgs__msg__Response__rosidl_typesupport_introspection_c__assign_function__Response__data,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  },
  {
    "slave_id",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_INT8,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    false,  // is key
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(om_msgs__msg__Response, slave_id),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  },
  {
    "func_code",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_INT8,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    false,  // is key
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(om_msgs__msg__Response, func_code),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  }
};

static const rosidl_typesupport_introspection_c__MessageMembers om_msgs__msg__Response__rosidl_typesupport_introspection_c__Response_message_members = {
  "om_msgs__msg",  // message namespace
  "Response",  // message name
  3,  // number of fields
  sizeof(om_msgs__msg__Response),
  false,  // has_any_key_member_
  om_msgs__msg__Response__rosidl_typesupport_introspection_c__Response_message_member_array,  // message members
  om_msgs__msg__Response__rosidl_typesupport_introspection_c__Response_init_function,  // function to initialize message memory (memory has to be allocated)
  om_msgs__msg__Response__rosidl_typesupport_introspection_c__Response_fini_function  // function to terminate message instance (will not free memory)
};

// this is not const since it must be initialized on first access
// since C does not allow non-integral compile-time constants
static rosidl_message_type_support_t om_msgs__msg__Response__rosidl_typesupport_introspection_c__Response_message_type_support_handle = {
  0,
  &om_msgs__msg__Response__rosidl_typesupport_introspection_c__Response_message_members,
  get_message_typesupport_handle_function,
  &om_msgs__msg__Response__get_type_hash,
  &om_msgs__msg__Response__get_type_description,
  &om_msgs__msg__Response__get_type_description_sources,
};

ROSIDL_TYPESUPPORT_INTROSPECTION_C_EXPORT_om_msgs
const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, om_msgs, msg, Response)() {
  if (!om_msgs__msg__Response__rosidl_typesupport_introspection_c__Response_message_type_support_handle.typesupport_identifier) {
    om_msgs__msg__Response__rosidl_typesupport_introspection_c__Response_message_type_support_handle.typesupport_identifier =
      rosidl_typesupport_introspection_c__identifier;
  }
  return &om_msgs__msg__Response__rosidl_typesupport_introspection_c__Response_message_type_support_handle;
}
#ifdef __cplusplus
}
#endif
