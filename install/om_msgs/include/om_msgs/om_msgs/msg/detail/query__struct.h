// generated from rosidl_generator_c/resource/idl__struct.h.em
// with input from om_msgs:msg/Query.idl
// generated code does not contain a copyright notice

// IWYU pragma: private, include "om_msgs/msg/query.h"


#ifndef OM_MSGS__MSG__DETAIL__QUERY__STRUCT_H_
#define OM_MSGS__MSG__DETAIL__QUERY__STRUCT_H_

#ifdef __cplusplus
extern "C"
{
#endif

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

// Constants defined in the message

/// Struct defined in msg/Query in the package om_msgs.
typedef struct om_msgs__msg__Query
{
  int8_t slave_id;
  int8_t func_code;
  int32_t write_addr;
  int32_t read_addr;
  int8_t write_num;
  int8_t read_num;
  int32_t data[64];
} om_msgs__msg__Query;

// Struct for a sequence of om_msgs__msg__Query.
typedef struct om_msgs__msg__Query__Sequence
{
  om_msgs__msg__Query * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} om_msgs__msg__Query__Sequence;

#ifdef __cplusplus
}
#endif

#endif  // OM_MSGS__MSG__DETAIL__QUERY__STRUCT_H_
