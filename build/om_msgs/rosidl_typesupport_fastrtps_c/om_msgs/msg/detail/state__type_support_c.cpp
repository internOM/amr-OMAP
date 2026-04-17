// generated from rosidl_typesupport_fastrtps_c/resource/idl__type_support_c.cpp.em
// with input from om_msgs:msg/State.idl
// generated code does not contain a copyright notice
#include "om_msgs/msg/detail/state__rosidl_typesupport_fastrtps_c.h"


#include <cassert>
#include <cstddef>
#include <limits>
#include <string>
#include "rosidl_typesupport_fastrtps_c/identifier.h"
#include "rosidl_typesupport_fastrtps_c/serialization_helpers.hpp"
#include "rosidl_typesupport_fastrtps_c/wstring_conversion.hpp"
#include "rosidl_typesupport_fastrtps_cpp/message_type_support.h"
#include "om_msgs/msg/rosidl_typesupport_fastrtps_c__visibility_control.h"
#include "om_msgs/msg/detail/state__struct.h"
#include "om_msgs/msg/detail/state__functions.h"
#include "fastcdr/Cdr.h"

#ifndef _WIN32
# pragma GCC diagnostic push
# pragma GCC diagnostic ignored "-Wunused-parameter"
# ifdef __clang__
#  pragma clang diagnostic ignored "-Wdeprecated-register"
#  pragma clang diagnostic ignored "-Wreturn-type-c-linkage"
# endif
#endif
#ifndef _WIN32
# pragma GCC diagnostic pop
#endif

// includes and forward declarations of message dependencies and their conversion functions

#if defined(__cplusplus)
extern "C"
{
#endif


// forward declare type support functions


using _State__ros_msg_type = om_msgs__msg__State;


ROSIDL_TYPESUPPORT_FASTRTPS_C_PUBLIC_om_msgs
bool cdr_serialize_om_msgs__msg__State(
  const om_msgs__msg__State * ros_message,
  eprosima::fastcdr::Cdr & cdr)
{
  // Field name: state_driver
  {
    cdr << ros_message->state_driver;
  }

  // Field name: state_mes
  {
    cdr << ros_message->state_mes;
  }

  // Field name: state_error
  {
    cdr << ros_message->state_error;
  }

  return true;
}

ROSIDL_TYPESUPPORT_FASTRTPS_C_PUBLIC_om_msgs
bool cdr_deserialize_om_msgs__msg__State(
  eprosima::fastcdr::Cdr & cdr,
  om_msgs__msg__State * ros_message)
{
  // Field name: state_driver
  {
    cdr >> ros_message->state_driver;
  }

  // Field name: state_mes
  {
    cdr >> ros_message->state_mes;
  }

  // Field name: state_error
  {
    cdr >> ros_message->state_error;
  }

  return true;
}  // NOLINT(readability/fn_size)


ROSIDL_TYPESUPPORT_FASTRTPS_C_PUBLIC_om_msgs
size_t get_serialized_size_om_msgs__msg__State(
  const void * untyped_ros_message,
  size_t current_alignment)
{
  const _State__ros_msg_type * ros_message = static_cast<const _State__ros_msg_type *>(untyped_ros_message);
  (void)ros_message;
  size_t initial_alignment = current_alignment;

  const size_t padding = 4;
  const size_t wchar_size = 4;
  (void)padding;
  (void)wchar_size;

  // Field name: state_driver
  {
    size_t item_size = sizeof(ros_message->state_driver);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Field name: state_mes
  {
    size_t item_size = sizeof(ros_message->state_mes);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Field name: state_error
  {
    size_t item_size = sizeof(ros_message->state_error);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  return current_alignment - initial_alignment;
}


ROSIDL_TYPESUPPORT_FASTRTPS_C_PUBLIC_om_msgs
size_t max_serialized_size_om_msgs__msg__State(
  bool & full_bounded,
  bool & is_plain,
  size_t current_alignment)
{
  size_t initial_alignment = current_alignment;

  const size_t padding = 4;
  const size_t wchar_size = 4;
  size_t last_member_size = 0;
  (void)last_member_size;
  (void)padding;
  (void)wchar_size;

  full_bounded = true;
  is_plain = true;

  // Field name: state_driver
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint8_t);
    current_alignment += array_size * sizeof(uint8_t);
  }

  // Field name: state_mes
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint8_t);
    current_alignment += array_size * sizeof(uint8_t);
  }

  // Field name: state_error
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint8_t);
    current_alignment += array_size * sizeof(uint8_t);
  }


  size_t ret_val = current_alignment - initial_alignment;
  if (is_plain) {
    // All members are plain, and type is not empty.
    // We still need to check that the in-memory alignment
    // is the same as the CDR mandated alignment.
    using DataType = om_msgs__msg__State;
    is_plain =
      (
      offsetof(DataType, state_error) +
      last_member_size
      ) == ret_val;
  }
  return ret_val;
}

ROSIDL_TYPESUPPORT_FASTRTPS_C_PUBLIC_om_msgs
bool cdr_serialize_key_om_msgs__msg__State(
  const om_msgs__msg__State * ros_message,
  eprosima::fastcdr::Cdr & cdr)
{
  // Field name: state_driver
  {
    cdr << ros_message->state_driver;
  }

  // Field name: state_mes
  {
    cdr << ros_message->state_mes;
  }

  // Field name: state_error
  {
    cdr << ros_message->state_error;
  }

  return true;
}

ROSIDL_TYPESUPPORT_FASTRTPS_C_PUBLIC_om_msgs
size_t get_serialized_size_key_om_msgs__msg__State(
  const void * untyped_ros_message,
  size_t current_alignment)
{
  const _State__ros_msg_type * ros_message = static_cast<const _State__ros_msg_type *>(untyped_ros_message);
  (void)ros_message;

  size_t initial_alignment = current_alignment;

  const size_t padding = 4;
  const size_t wchar_size = 4;
  (void)padding;
  (void)wchar_size;

  // Field name: state_driver
  {
    size_t item_size = sizeof(ros_message->state_driver);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Field name: state_mes
  {
    size_t item_size = sizeof(ros_message->state_mes);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Field name: state_error
  {
    size_t item_size = sizeof(ros_message->state_error);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  return current_alignment - initial_alignment;
}

ROSIDL_TYPESUPPORT_FASTRTPS_C_PUBLIC_om_msgs
size_t max_serialized_size_key_om_msgs__msg__State(
  bool & full_bounded,
  bool & is_plain,
  size_t current_alignment)
{
  size_t initial_alignment = current_alignment;

  const size_t padding = 4;
  const size_t wchar_size = 4;
  size_t last_member_size = 0;
  (void)last_member_size;
  (void)padding;
  (void)wchar_size;

  full_bounded = true;
  is_plain = true;
  // Field name: state_driver
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint8_t);
    current_alignment += array_size * sizeof(uint8_t);
  }

  // Field name: state_mes
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint8_t);
    current_alignment += array_size * sizeof(uint8_t);
  }

  // Field name: state_error
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint8_t);
    current_alignment += array_size * sizeof(uint8_t);
  }

  size_t ret_val = current_alignment - initial_alignment;
  if (is_plain) {
    // All members are plain, and type is not empty.
    // We still need to check that the in-memory alignment
    // is the same as the CDR mandated alignment.
    using DataType = om_msgs__msg__State;
    is_plain =
      (
      offsetof(DataType, state_error) +
      last_member_size
      ) == ret_val;
  }
  return ret_val;
}


static bool _State__cdr_serialize(
  const void * untyped_ros_message,
  eprosima::fastcdr::Cdr & cdr)
{
  if (!untyped_ros_message) {
    fprintf(stderr, "ros message handle is null\n");
    return false;
  }
  const om_msgs__msg__State * ros_message = static_cast<const om_msgs__msg__State *>(untyped_ros_message);
  (void)ros_message;
  return cdr_serialize_om_msgs__msg__State(ros_message, cdr);
}

static bool _State__cdr_deserialize(
  eprosima::fastcdr::Cdr & cdr,
  void * untyped_ros_message)
{
  if (!untyped_ros_message) {
    fprintf(stderr, "ros message handle is null\n");
    return false;
  }
  om_msgs__msg__State * ros_message = static_cast<om_msgs__msg__State *>(untyped_ros_message);
  (void)ros_message;
  return cdr_deserialize_om_msgs__msg__State(cdr, ros_message);
}

static uint32_t _State__get_serialized_size(const void * untyped_ros_message)
{
  return static_cast<uint32_t>(
    get_serialized_size_om_msgs__msg__State(
      untyped_ros_message, 0));
}

static size_t _State__max_serialized_size(char & bounds_info)
{
  bool full_bounded;
  bool is_plain;
  size_t ret_val;

  ret_val = max_serialized_size_om_msgs__msg__State(
    full_bounded, is_plain, 0);

  bounds_info =
    is_plain ? ROSIDL_TYPESUPPORT_FASTRTPS_PLAIN_TYPE :
    full_bounded ? ROSIDL_TYPESUPPORT_FASTRTPS_BOUNDED_TYPE : ROSIDL_TYPESUPPORT_FASTRTPS_UNBOUNDED_TYPE;
  return ret_val;
}


static message_type_support_callbacks_t __callbacks_State = {
  "om_msgs::msg",
  "State",
  _State__cdr_serialize,
  _State__cdr_deserialize,
  _State__get_serialized_size,
  _State__max_serialized_size,
  nullptr
};

static rosidl_message_type_support_t _State__type_support = {
  rosidl_typesupport_fastrtps_c__identifier,
  &__callbacks_State,
  get_message_typesupport_handle_function,
  &om_msgs__msg__State__get_type_hash,
  &om_msgs__msg__State__get_type_description,
  &om_msgs__msg__State__get_type_description_sources,
};

const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_fastrtps_c, om_msgs, msg, State)() {
  return &_State__type_support;
}

#if defined(__cplusplus)
}
#endif
