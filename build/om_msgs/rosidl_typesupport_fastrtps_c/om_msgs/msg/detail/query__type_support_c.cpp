// generated from rosidl_typesupport_fastrtps_c/resource/idl__type_support_c.cpp.em
// with input from om_msgs:msg/Query.idl
// generated code does not contain a copyright notice
#include "om_msgs/msg/detail/query__rosidl_typesupport_fastrtps_c.h"


#include <cassert>
#include <cstddef>
#include <limits>
#include <string>
#include "rosidl_typesupport_fastrtps_c/identifier.h"
#include "rosidl_typesupport_fastrtps_c/serialization_helpers.hpp"
#include "rosidl_typesupport_fastrtps_c/wstring_conversion.hpp"
#include "rosidl_typesupport_fastrtps_cpp/message_type_support.h"
#include "om_msgs/msg/rosidl_typesupport_fastrtps_c__visibility_control.h"
#include "om_msgs/msg/detail/query__struct.h"
#include "om_msgs/msg/detail/query__functions.h"
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


using _Query__ros_msg_type = om_msgs__msg__Query;


ROSIDL_TYPESUPPORT_FASTRTPS_C_PUBLIC_om_msgs
bool cdr_serialize_om_msgs__msg__Query(
  const om_msgs__msg__Query * ros_message,
  eprosima::fastcdr::Cdr & cdr)
{
  // Field name: slave_id
  {
    cdr << ros_message->slave_id;
  }

  // Field name: func_code
  {
    cdr << ros_message->func_code;
  }

  // Field name: write_addr
  {
    cdr << ros_message->write_addr;
  }

  // Field name: read_addr
  {
    cdr << ros_message->read_addr;
  }

  // Field name: write_num
  {
    cdr << ros_message->write_num;
  }

  // Field name: read_num
  {
    cdr << ros_message->read_num;
  }

  // Field name: data
  {
    size_t size = 64;
    auto array_ptr = ros_message->data;
    cdr.serialize_array(array_ptr, size);
  }

  return true;
}

ROSIDL_TYPESUPPORT_FASTRTPS_C_PUBLIC_om_msgs
bool cdr_deserialize_om_msgs__msg__Query(
  eprosima::fastcdr::Cdr & cdr,
  om_msgs__msg__Query * ros_message)
{
  // Field name: slave_id
  {
    cdr >> ros_message->slave_id;
  }

  // Field name: func_code
  {
    cdr >> ros_message->func_code;
  }

  // Field name: write_addr
  {
    cdr >> ros_message->write_addr;
  }

  // Field name: read_addr
  {
    cdr >> ros_message->read_addr;
  }

  // Field name: write_num
  {
    cdr >> ros_message->write_num;
  }

  // Field name: read_num
  {
    cdr >> ros_message->read_num;
  }

  // Field name: data
  {
    size_t size = 64;
    auto array_ptr = ros_message->data;
    cdr.deserialize_array(array_ptr, size);
  }

  return true;
}  // NOLINT(readability/fn_size)


ROSIDL_TYPESUPPORT_FASTRTPS_C_PUBLIC_om_msgs
size_t get_serialized_size_om_msgs__msg__Query(
  const void * untyped_ros_message,
  size_t current_alignment)
{
  const _Query__ros_msg_type * ros_message = static_cast<const _Query__ros_msg_type *>(untyped_ros_message);
  (void)ros_message;
  size_t initial_alignment = current_alignment;

  const size_t padding = 4;
  const size_t wchar_size = 4;
  (void)padding;
  (void)wchar_size;

  // Field name: slave_id
  {
    size_t item_size = sizeof(ros_message->slave_id);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Field name: func_code
  {
    size_t item_size = sizeof(ros_message->func_code);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Field name: write_addr
  {
    size_t item_size = sizeof(ros_message->write_addr);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Field name: read_addr
  {
    size_t item_size = sizeof(ros_message->read_addr);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Field name: write_num
  {
    size_t item_size = sizeof(ros_message->write_num);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Field name: read_num
  {
    size_t item_size = sizeof(ros_message->read_num);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Field name: data
  {
    size_t array_size = 64;
    auto array_ptr = ros_message->data;
    (void)array_ptr;
    size_t item_size = sizeof(array_ptr[0]);
    current_alignment += array_size * item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  return current_alignment - initial_alignment;
}


ROSIDL_TYPESUPPORT_FASTRTPS_C_PUBLIC_om_msgs
size_t max_serialized_size_om_msgs__msg__Query(
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

  // Field name: slave_id
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint8_t);
    current_alignment += array_size * sizeof(uint8_t);
  }

  // Field name: func_code
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint8_t);
    current_alignment += array_size * sizeof(uint8_t);
  }

  // Field name: write_addr
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }

  // Field name: read_addr
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }

  // Field name: write_num
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint8_t);
    current_alignment += array_size * sizeof(uint8_t);
  }

  // Field name: read_num
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint8_t);
    current_alignment += array_size * sizeof(uint8_t);
  }

  // Field name: data
  {
    size_t array_size = 64;
    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }


  size_t ret_val = current_alignment - initial_alignment;
  if (is_plain) {
    // All members are plain, and type is not empty.
    // We still need to check that the in-memory alignment
    // is the same as the CDR mandated alignment.
    using DataType = om_msgs__msg__Query;
    is_plain =
      (
      offsetof(DataType, data) +
      last_member_size
      ) == ret_val;
  }
  return ret_val;
}

ROSIDL_TYPESUPPORT_FASTRTPS_C_PUBLIC_om_msgs
bool cdr_serialize_key_om_msgs__msg__Query(
  const om_msgs__msg__Query * ros_message,
  eprosima::fastcdr::Cdr & cdr)
{
  // Field name: slave_id
  {
    cdr << ros_message->slave_id;
  }

  // Field name: func_code
  {
    cdr << ros_message->func_code;
  }

  // Field name: write_addr
  {
    cdr << ros_message->write_addr;
  }

  // Field name: read_addr
  {
    cdr << ros_message->read_addr;
  }

  // Field name: write_num
  {
    cdr << ros_message->write_num;
  }

  // Field name: read_num
  {
    cdr << ros_message->read_num;
  }

  // Field name: data
  {
    size_t size = 64;
    auto array_ptr = ros_message->data;
    cdr.serialize_array(array_ptr, size);
  }

  return true;
}

ROSIDL_TYPESUPPORT_FASTRTPS_C_PUBLIC_om_msgs
size_t get_serialized_size_key_om_msgs__msg__Query(
  const void * untyped_ros_message,
  size_t current_alignment)
{
  const _Query__ros_msg_type * ros_message = static_cast<const _Query__ros_msg_type *>(untyped_ros_message);
  (void)ros_message;

  size_t initial_alignment = current_alignment;

  const size_t padding = 4;
  const size_t wchar_size = 4;
  (void)padding;
  (void)wchar_size;

  // Field name: slave_id
  {
    size_t item_size = sizeof(ros_message->slave_id);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Field name: func_code
  {
    size_t item_size = sizeof(ros_message->func_code);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Field name: write_addr
  {
    size_t item_size = sizeof(ros_message->write_addr);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Field name: read_addr
  {
    size_t item_size = sizeof(ros_message->read_addr);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Field name: write_num
  {
    size_t item_size = sizeof(ros_message->write_num);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Field name: read_num
  {
    size_t item_size = sizeof(ros_message->read_num);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Field name: data
  {
    size_t array_size = 64;
    auto array_ptr = ros_message->data;
    (void)array_ptr;
    size_t item_size = sizeof(array_ptr[0]);
    current_alignment += array_size * item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  return current_alignment - initial_alignment;
}

ROSIDL_TYPESUPPORT_FASTRTPS_C_PUBLIC_om_msgs
size_t max_serialized_size_key_om_msgs__msg__Query(
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
  // Field name: slave_id
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint8_t);
    current_alignment += array_size * sizeof(uint8_t);
  }

  // Field name: func_code
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint8_t);
    current_alignment += array_size * sizeof(uint8_t);
  }

  // Field name: write_addr
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }

  // Field name: read_addr
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }

  // Field name: write_num
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint8_t);
    current_alignment += array_size * sizeof(uint8_t);
  }

  // Field name: read_num
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint8_t);
    current_alignment += array_size * sizeof(uint8_t);
  }

  // Field name: data
  {
    size_t array_size = 64;
    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }

  size_t ret_val = current_alignment - initial_alignment;
  if (is_plain) {
    // All members are plain, and type is not empty.
    // We still need to check that the in-memory alignment
    // is the same as the CDR mandated alignment.
    using DataType = om_msgs__msg__Query;
    is_plain =
      (
      offsetof(DataType, data) +
      last_member_size
      ) == ret_val;
  }
  return ret_val;
}


static bool _Query__cdr_serialize(
  const void * untyped_ros_message,
  eprosima::fastcdr::Cdr & cdr)
{
  if (!untyped_ros_message) {
    fprintf(stderr, "ros message handle is null\n");
    return false;
  }
  const om_msgs__msg__Query * ros_message = static_cast<const om_msgs__msg__Query *>(untyped_ros_message);
  (void)ros_message;
  return cdr_serialize_om_msgs__msg__Query(ros_message, cdr);
}

static bool _Query__cdr_deserialize(
  eprosima::fastcdr::Cdr & cdr,
  void * untyped_ros_message)
{
  if (!untyped_ros_message) {
    fprintf(stderr, "ros message handle is null\n");
    return false;
  }
  om_msgs__msg__Query * ros_message = static_cast<om_msgs__msg__Query *>(untyped_ros_message);
  (void)ros_message;
  return cdr_deserialize_om_msgs__msg__Query(cdr, ros_message);
}

static uint32_t _Query__get_serialized_size(const void * untyped_ros_message)
{
  return static_cast<uint32_t>(
    get_serialized_size_om_msgs__msg__Query(
      untyped_ros_message, 0));
}

static size_t _Query__max_serialized_size(char & bounds_info)
{
  bool full_bounded;
  bool is_plain;
  size_t ret_val;

  ret_val = max_serialized_size_om_msgs__msg__Query(
    full_bounded, is_plain, 0);

  bounds_info =
    is_plain ? ROSIDL_TYPESUPPORT_FASTRTPS_PLAIN_TYPE :
    full_bounded ? ROSIDL_TYPESUPPORT_FASTRTPS_BOUNDED_TYPE : ROSIDL_TYPESUPPORT_FASTRTPS_UNBOUNDED_TYPE;
  return ret_val;
}


static message_type_support_callbacks_t __callbacks_Query = {
  "om_msgs::msg",
  "Query",
  _Query__cdr_serialize,
  _Query__cdr_deserialize,
  _Query__get_serialized_size,
  _Query__max_serialized_size,
  nullptr
};

static rosidl_message_type_support_t _Query__type_support = {
  rosidl_typesupport_fastrtps_c__identifier,
  &__callbacks_Query,
  get_message_typesupport_handle_function,
  &om_msgs__msg__Query__get_type_hash,
  &om_msgs__msg__Query__get_type_description,
  &om_msgs__msg__Query__get_type_description_sources,
};

const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_fastrtps_c, om_msgs, msg, Query)() {
  return &_Query__type_support;
}

#if defined(__cplusplus)
}
#endif
