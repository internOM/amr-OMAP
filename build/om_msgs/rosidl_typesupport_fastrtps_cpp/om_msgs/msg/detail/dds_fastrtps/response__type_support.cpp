// generated from rosidl_typesupport_fastrtps_cpp/resource/idl__type_support.cpp.em
// with input from om_msgs:msg/Response.idl
// generated code does not contain a copyright notice
#include "om_msgs/msg/detail/response__rosidl_typesupport_fastrtps_cpp.hpp"
#include "om_msgs/msg/detail/response__functions.h"
#include "om_msgs/msg/detail/response__struct.hpp"

#include <cstddef>
#include <limits>
#include <stdexcept>
#include <string>
#include "rosidl_typesupport_cpp/message_type_support.hpp"
#include "rosidl_typesupport_fastrtps_cpp/identifier.hpp"
#include "rosidl_typesupport_fastrtps_cpp/message_type_support.h"
#include "rosidl_typesupport_fastrtps_cpp/message_type_support_decl.hpp"
#include "rosidl_typesupport_fastrtps_cpp/serialization_helpers.hpp"
#include "rosidl_typesupport_fastrtps_cpp/wstring_conversion.hpp"
#include "fastcdr/Cdr.h"


// forward declaration of message dependencies and their conversion functions

namespace om_msgs
{

namespace msg
{

namespace typesupport_fastrtps_cpp
{


bool
ROSIDL_TYPESUPPORT_FASTRTPS_CPP_PUBLIC_om_msgs
cdr_serialize(
  const om_msgs::msg::Response & ros_message,
  eprosima::fastcdr::Cdr & cdr)
{
  // Member: data
  {
    cdr << ros_message.data;
  }

  // Member: slave_id
  cdr << ros_message.slave_id;

  // Member: func_code
  cdr << ros_message.func_code;

  return true;
}

bool
ROSIDL_TYPESUPPORT_FASTRTPS_CPP_PUBLIC_om_msgs
cdr_deserialize(
  eprosima::fastcdr::Cdr & cdr,
  om_msgs::msg::Response & ros_message)
{
  // Member: data
  {
    cdr >> ros_message.data;
  }

  // Member: slave_id
  cdr >> ros_message.slave_id;

  // Member: func_code
  cdr >> ros_message.func_code;

  return true;
}  // NOLINT(readability/fn_size)


size_t
ROSIDL_TYPESUPPORT_FASTRTPS_CPP_PUBLIC_om_msgs
get_serialized_size(
  const om_msgs::msg::Response & ros_message,
  size_t current_alignment)
{
  size_t initial_alignment = current_alignment;

  const size_t padding = 4;
  const size_t wchar_size = 4;
  (void)padding;
  (void)wchar_size;

  // Member: data
  {
    size_t array_size = 64;
    size_t item_size = sizeof(ros_message.data[0]);
    current_alignment += array_size * item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Member: slave_id
  {
    size_t item_size = sizeof(ros_message.slave_id);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Member: func_code
  {
    size_t item_size = sizeof(ros_message.func_code);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  return current_alignment - initial_alignment;
}


size_t
ROSIDL_TYPESUPPORT_FASTRTPS_CPP_PUBLIC_om_msgs
max_serialized_size_Response(
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

  // Member: data
  {
    size_t array_size = 64;
    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }
  // Member: slave_id
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint8_t);
    current_alignment += array_size * sizeof(uint8_t);
  }
  // Member: func_code
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
    using DataType = om_msgs::msg::Response;
    is_plain =
      (
      offsetof(DataType, func_code) +
      last_member_size
      ) == ret_val;
  }

  return ret_val;
}

bool
ROSIDL_TYPESUPPORT_FASTRTPS_CPP_PUBLIC_om_msgs
cdr_serialize_key(
  const om_msgs::msg::Response & ros_message,
  eprosima::fastcdr::Cdr & cdr)
{
  // Member: data
  {
    cdr << ros_message.data;
  }

  // Member: slave_id
  cdr << ros_message.slave_id;

  // Member: func_code
  cdr << ros_message.func_code;

  return true;
}

size_t
ROSIDL_TYPESUPPORT_FASTRTPS_CPP_PUBLIC_om_msgs
get_serialized_size_key(
  const om_msgs::msg::Response & ros_message,
  size_t current_alignment)
{
  size_t initial_alignment = current_alignment;

  const size_t padding = 4;
  const size_t wchar_size = 4;
  (void)padding;
  (void)wchar_size;

  // Member: data
  {
    size_t array_size = 64;
    size_t item_size = sizeof(ros_message.data[0]);
    current_alignment += array_size * item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Member: slave_id
  {
    size_t item_size = sizeof(ros_message.slave_id);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Member: func_code
  {
    size_t item_size = sizeof(ros_message.func_code);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  return current_alignment - initial_alignment;
}

size_t
ROSIDL_TYPESUPPORT_FASTRTPS_CPP_PUBLIC_om_msgs
max_serialized_size_key_Response(
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

  // Member: data
  {
    size_t array_size = 64;
    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }

  // Member: slave_id
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint8_t);
    current_alignment += array_size * sizeof(uint8_t);
  }

  // Member: func_code
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
    using DataType = om_msgs::msg::Response;
    is_plain =
      (
      offsetof(DataType, func_code) +
      last_member_size
      ) == ret_val;
  }

  return ret_val;
}


static bool _Response__cdr_serialize(
  const void * untyped_ros_message,
  eprosima::fastcdr::Cdr & cdr)
{
  auto typed_message =
    static_cast<const om_msgs::msg::Response *>(
    untyped_ros_message);
  return cdr_serialize(*typed_message, cdr);
}

static bool _Response__cdr_deserialize(
  eprosima::fastcdr::Cdr & cdr,
  void * untyped_ros_message)
{
  auto typed_message =
    static_cast<om_msgs::msg::Response *>(
    untyped_ros_message);
  return cdr_deserialize(cdr, *typed_message);
}

static uint32_t _Response__get_serialized_size(
  const void * untyped_ros_message)
{
  auto typed_message =
    static_cast<const om_msgs::msg::Response *>(
    untyped_ros_message);
  return static_cast<uint32_t>(get_serialized_size(*typed_message, 0));
}

static size_t _Response__max_serialized_size(char & bounds_info)
{
  bool full_bounded;
  bool is_plain;
  size_t ret_val;

  ret_val = max_serialized_size_Response(full_bounded, is_plain, 0);

  bounds_info =
    is_plain ? ROSIDL_TYPESUPPORT_FASTRTPS_PLAIN_TYPE :
    full_bounded ? ROSIDL_TYPESUPPORT_FASTRTPS_BOUNDED_TYPE : ROSIDL_TYPESUPPORT_FASTRTPS_UNBOUNDED_TYPE;
  return ret_val;
}

static message_type_support_callbacks_t _Response__callbacks = {
  "om_msgs::msg",
  "Response",
  _Response__cdr_serialize,
  _Response__cdr_deserialize,
  _Response__get_serialized_size,
  _Response__max_serialized_size,
  nullptr
};

static rosidl_message_type_support_t _Response__handle = {
  rosidl_typesupport_fastrtps_cpp::typesupport_identifier,
  &_Response__callbacks,
  get_message_typesupport_handle_function,
  &om_msgs__msg__Response__get_type_hash,
  &om_msgs__msg__Response__get_type_description,
  &om_msgs__msg__Response__get_type_description_sources,
};

}  // namespace typesupport_fastrtps_cpp

}  // namespace msg

}  // namespace om_msgs

namespace rosidl_typesupport_fastrtps_cpp
{

template<>
ROSIDL_TYPESUPPORT_FASTRTPS_CPP_EXPORT_om_msgs
const rosidl_message_type_support_t *
get_message_type_support_handle<om_msgs::msg::Response>()
{
  return &om_msgs::msg::typesupport_fastrtps_cpp::_Response__handle;
}

}  // namespace rosidl_typesupport_fastrtps_cpp

#ifdef __cplusplus
extern "C"
{
#endif

const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_fastrtps_cpp, om_msgs, msg, Response)() {
  return &om_msgs::msg::typesupport_fastrtps_cpp::_Response__handle;
}

#ifdef __cplusplus
}
#endif
