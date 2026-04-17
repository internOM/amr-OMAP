// generated from rosidl_generator_c/resource/idl__struct.h.em
// with input from om_msgs:msg/State.idl
// generated code does not contain a copyright notice

// IWYU pragma: private, include "om_msgs/msg/state.h"


#ifndef OM_MSGS__MSG__DETAIL__STATE__STRUCT_H_
#define OM_MSGS__MSG__DETAIL__STATE__STRUCT_H_

#ifdef __cplusplus
extern "C"
{
#endif

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

// Constants defined in the message

/// Struct defined in msg/State in the package om_msgs.
typedef struct om_msgs__msg__State
{
  int8_t state_driver;
  int8_t state_mes;
  int8_t state_error;
} om_msgs__msg__State;

// Struct for a sequence of om_msgs__msg__State.
typedef struct om_msgs__msg__State__Sequence
{
  om_msgs__msg__State * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} om_msgs__msg__State__Sequence;

#ifdef __cplusplus
}
#endif

#endif  // OM_MSGS__MSG__DETAIL__STATE__STRUCT_H_
