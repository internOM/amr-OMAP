// generated from rosidl_typesupport_fastrtps_c/resource/idl__rosidl_typesupport_fastrtps_c.h.em
// with input from om_msgs:msg/Response.idl
// generated code does not contain a copyright notice
#ifndef OM_MSGS__MSG__DETAIL__RESPONSE__ROSIDL_TYPESUPPORT_FASTRTPS_C_H_
#define OM_MSGS__MSG__DETAIL__RESPONSE__ROSIDL_TYPESUPPORT_FASTRTPS_C_H_


#include <stddef.h>
#include "rosidl_runtime_c/message_type_support_struct.h"
#include "rosidl_typesupport_interface/macros.h"
#include "om_msgs/msg/rosidl_typesupport_fastrtps_c__visibility_control.h"
#include "om_msgs/msg/detail/response__struct.h"
#include "fastcdr/Cdr.h"

#ifdef __cplusplus
extern "C"
{
#endif

ROSIDL_TYPESUPPORT_FASTRTPS_C_PUBLIC_om_msgs
bool cdr_serialize_om_msgs__msg__Response(
  const om_msgs__msg__Response * ros_message,
  eprosima::fastcdr::Cdr & cdr);

ROSIDL_TYPESUPPORT_FASTRTPS_C_PUBLIC_om_msgs
bool cdr_deserialize_om_msgs__msg__Response(
  eprosima::fastcdr::Cdr &,
  om_msgs__msg__Response * ros_message);

ROSIDL_TYPESUPPORT_FASTRTPS_C_PUBLIC_om_msgs
size_t get_serialized_size_om_msgs__msg__Response(
  const void * untyped_ros_message,
  size_t current_alignment);

ROSIDL_TYPESUPPORT_FASTRTPS_C_PUBLIC_om_msgs
size_t max_serialized_size_om_msgs__msg__Response(
  bool & full_bounded,
  bool & is_plain,
  size_t current_alignment);

ROSIDL_TYPESUPPORT_FASTRTPS_C_PUBLIC_om_msgs
bool cdr_serialize_key_om_msgs__msg__Response(
  const om_msgs__msg__Response * ros_message,
  eprosima::fastcdr::Cdr & cdr);

ROSIDL_TYPESUPPORT_FASTRTPS_C_PUBLIC_om_msgs
size_t get_serialized_size_key_om_msgs__msg__Response(
  const void * untyped_ros_message,
  size_t current_alignment);

ROSIDL_TYPESUPPORT_FASTRTPS_C_PUBLIC_om_msgs
size_t max_serialized_size_key_om_msgs__msg__Response(
  bool & full_bounded,
  bool & is_plain,
  size_t current_alignment);

ROSIDL_TYPESUPPORT_FASTRTPS_C_PUBLIC_om_msgs
const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_fastrtps_c, om_msgs, msg, Response)();

#ifdef __cplusplus
}
#endif

#endif  // OM_MSGS__MSG__DETAIL__RESPONSE__ROSIDL_TYPESUPPORT_FASTRTPS_C_H_
