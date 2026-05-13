// generated from rosidl_typesupport_introspection_c/resource/idl__type_support.c.em
// with input from om_msgs:msg/State.idl
// generated code does not contain a copyright notice

#include <stddef.h>
#include "om_msgs/msg/detail/state__rosidl_typesupport_introspection_c.h"
#include "om_msgs/msg/rosidl_typesupport_introspection_c__visibility_control.h"
#include "rosidl_typesupport_introspection_c/field_types.h"
#include "rosidl_typesupport_introspection_c/identifier.h"
#include "rosidl_typesupport_introspection_c/message_introspection.h"
#include "om_msgs/msg/detail/state__functions.h"
#include "om_msgs/msg/detail/state__struct.h"


#ifdef __cplusplus
extern "C"
{
#endif

void om_msgs__msg__State__rosidl_typesupport_introspection_c__State_init_function(
  void * message_memory, enum rosidl_runtime_c__message_initialization _init)
{
  // TODO(karsten1987): initializers are not yet implemented for typesupport c
  // see https://github.com/ros2/ros2/issues/397
  (void) _init;
  om_msgs__msg__State__init(message_memory);
}

void om_msgs__msg__State__rosidl_typesupport_introspection_c__State_fini_function(void * message_memory)
{
  om_msgs__msg__State__fini(message_memory);
}

static rosidl_typesupport_introspection_c__MessageMember om_msgs__msg__State__rosidl_typesupport_introspection_c__State_message_member_array[3] = {
  {
    "state_driver",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_INT8,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    false,  // is key
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(om_msgs__msg__State, state_driver),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  },
  {
    "state_mes",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_INT8,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    false,  // is key
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(om_msgs__msg__State, state_mes),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  },
  {
    "state_error",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_INT8,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    false,  // is key
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(om_msgs__msg__State, state_error),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  }
};

static const rosidl_typesupport_introspection_c__MessageMembers om_msgs__msg__State__rosidl_typesupport_introspection_c__State_message_members = {
  "om_msgs__msg",  // message namespace
  "State",  // message name
  3,  // number of fields
  sizeof(om_msgs__msg__State),
  false,  // has_any_key_member_
  om_msgs__msg__State__rosidl_typesupport_introspection_c__State_message_member_array,  // message members
  om_msgs__msg__State__rosidl_typesupport_introspection_c__State_init_function,  // function to initialize message memory (memory has to be allocated)
  om_msgs__msg__State__rosidl_typesupport_introspection_c__State_fini_function  // function to terminate message instance (will not free memory)
};

// this is not const since it must be initialized on first access
// since C does not allow non-integral compile-time constants
static rosidl_message_type_support_t om_msgs__msg__State__rosidl_typesupport_introspection_c__State_message_type_support_handle = {
  0,
  &om_msgs__msg__State__rosidl_typesupport_introspection_c__State_message_members,
  get_message_typesupport_handle_function,
  &om_msgs__msg__State__get_type_hash,
  &om_msgs__msg__State__get_type_description,
  &om_msgs__msg__State__get_type_description_sources,
};

ROSIDL_TYPESUPPORT_INTROSPECTION_C_EXPORT_om_msgs
const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, om_msgs, msg, State)() {
  if (!om_msgs__msg__State__rosidl_typesupport_introspection_c__State_message_type_support_handle.typesupport_identifier) {
    om_msgs__msg__State__rosidl_typesupport_introspection_c__State_message_type_support_handle.typesupport_identifier =
      rosidl_typesupport_introspection_c__identifier;
  }
  return &om_msgs__msg__State__rosidl_typesupport_introspection_c__State_message_type_support_handle;
}
#ifdef __cplusplus
}
#endif
