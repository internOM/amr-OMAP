// generated from rosidl_typesupport_fastrtps_cpp/resource/idl__type_support.cpp.em
// with input from om_msgs:msg/Query.idl
// generated code does not contain a copyright notice
#include "om_msgs/msg/detail/query__rosidl_typesupport_fastrtps_cpp.hpp"
#include "om_msgs/msg/detail/query__functions.h"
#include "om_msgs/msg/detail/query__struct.hpp"

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
  const om_msgs::msg::Query & ros_message,
  eprosima::fastcdr::Cdr & cdr)
{
  // Member: slave_id
  cdr << ros_message.slave_id;

  // Member: func_code
  cdr << ros_message.func_code;

  // Member: write_addr
  cdr << ros_message.write_addr;

  // Member: read_addr
  cdr << ros_message.read_addr;

  // Member: write_num
  cdr << ros_message.write_num;

  // Member: read_num
  cdr << ros_message.read_num;

  // Member: data
  {
    cdr << ros_message.data;
  }

  return true;
}

bool
ROSIDL_TYPESUPPORT_FASTRTPS_CPP_PUBLIC_om_msgs
cdr_deserialize(
  eprosima::fastcdr::Cdr & cdr,
  om_msgs::msg::Query & ros_message)
{
  // Member: slave_id
  cdr >> ros_message.slave_id;

  // Member: func_code
  cdr >> ros_message.func_code;

  // Member: write_addr
  cdr >> ros_message.write_addr;

  // Member: read_addr
  cdr >> ros_message.read_addr;

  // Member: write_num
  cdr >> ros_message.write_num;

  // Member: read_num
  cdr >> ros_message.read_num;

  // Member: data
  {
    cdr >> ros_message.data;
  }

  return true;
}  // NOLINT(readability/fn_size)


size_t
ROSIDL_TYPESUPPORT_FASTRTPS_CPP_PUBLIC_om_msgs
get_serialized_size(
  const om_msgs::msg::Query & ros_message,
  size_t current_alignment)
{
  size_t initial_alignment = current_alignment;

  const size_t padding = 4;
  const size_t wchar_size = 4;
  (void)padding;
  (void)wchar_size;

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

  // Member: write_addr
  {
    size_t item_size = sizeof(ros_message.write_addr);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Member: read_addr
  {
    size_t item_size = sizeof(ros_message.read_addr);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Member: write_num
  {
    size_t item_size = sizeof(ros_message.write_num);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Member: read_num
  {
    size_t item_size = sizeof(ros_message.read_num);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Member: data
  {
    size_t array_size = 64;
    size_t item_size = sizeof(ros_message.data[0]);
    current_alignment += array_size * item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  return current_alignment - initial_alignment;
}


size_t
ROSIDL_TYPESUPPORT_FASTRTPS_CPP_PUBLIC_om_msgs
max_serialized_size_Query(
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
  // Member: write_addr
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }
  // Member: read_addr
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }
  // Member: write_num
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint8_t);
    current_alignment += array_size * sizeof(uint8_t);
  }
  // Member: read_num
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint8_t);
    current_alignment += array_size * sizeof(uint8_t);
  }
  // Member: data
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
    using DataType = om_msgs::msg::Query;
    is_plain =
      (
      offsetof(DataType, data) +
      last_member_size
      ) == ret_val;
  }

  return ret_val;
}

bool
ROSIDL_TYPESUPPORT_FASTRTPS_CPP_PUBLIC_om_msgs
cdr_serialize_key(
  const om_msgs::msg::Query & ros_message,
  eprosima::fastcdr::Cdr & cdr)
{
  // Member: slave_id
  cdr << ros_message.slave_id;

  // Member: func_code
  cdr << ros_message.func_code;

  // Member: write_addr
  cdr << ros_message.write_addr;

  // Member: read_addr
  cdr << ros_message.read_addr;

  // Member: write_num
  cdr << ros_message.write_num;

  // Member: read_num
  cdr << ros_message.read_num;

  // Member: data
  {
    cdr << ros_message.data;
  }

  return true;
}

size_t
ROSIDL_TYPESUPPORT_FASTRTPS_CPP_PUBLIC_om_msgs
get_serialized_size_key(
  const om_msgs::msg::Query & ros_message,
  size_t current_alignment)
{
  size_t initial_alignment = current_alignment;

  const size_t padding = 4;
  const size_t wchar_size = 4;
  (void)padding;
  (void)wchar_size;

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

  // Member: write_addr
  {
    size_t item_size = sizeof(ros_message.write_addr);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Member: read_addr
  {
    size_t item_size = sizeof(ros_message.read_addr);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Member: write_num
  {
    size_t item_size = sizeof(ros_message.write_num);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Member: read_num
  {
    size_t item_size = sizeof(ros_message.read_num);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Member: data
  {
    size_t array_size = 64;
    size_t item_size = sizeof(ros_message.data[0]);
    current_alignment += array_size * item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  return current_alignment - initial_alignment;
}

size_t
ROSIDL_TYPESUPPORT_FASTRTPS_CPP_PUBLIC_om_msgs
max_serialized_size_key_Query(
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

  // Member: write_addr
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }

  // Member: read_addr
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }

  // Member: write_num
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint8_t);
    current_alignment += array_size * sizeof(uint8_t);
  }

  // Member: read_num
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint8_t);
    current_alignment += array_size * sizeof(uint8_t);
  }

  // Member: data
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
    using DataType = om_msgs::msg::Query;
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
  auto typed_message =
    static_cast<const om_msgs::msg::Query *>(
    untyped_ros_message);
  return cdr_serialize(*typed_message, cdr);
}

static bool _Query__cdr_deserialize(
  eprosima::fastcdr::Cdr & cdr,
  void * untyped_ros_message)
{
  auto typed_message =
    static_cast<om_msgs::msg::Query *>(
    untyped_ros_message);
  return cdr_deserialize(cdr, *typed_message);
}

static uint32_t _Query__get_serialized_size(
  const void * untyped_ros_message)
{
  auto typed_message =
    static_cast<const om_msgs::msg::Query *>(
    untyped_ros_message);
  return static_cast<uint32_t>(get_serialized_size(*typed_message, 0));
}

static size_t _Query__max_serialized_size(char & bounds_info)
{
  bool full_bounded;
  bool is_plain;
  size_t ret_val;

  ret_val = max_serialized_size_Query(full_bounded, is_plain, 0);

  bounds_info =
    is_plain ? ROSIDL_TYPESUPPORT_FASTRTPS_PLAIN_TYPE :
    full_bounded ? ROSIDL_TYPESUPPORT_FASTRTPS_BOUNDED_TYPE : ROSIDL_TYPESUPPORT_FASTRTPS_UNBOUNDED_TYPE;
  return ret_val;
}

static message_type_support_callbacks_t _Query__callbacks = {
  "om_msgs::msg",
  "Query",
  _Query__cdr_serialize,
  _Query__cdr_deserialize,
  _Query__get_serialized_size,
  _Query__max_serialized_size,
  nullptr
};

static rosidl_message_type_support_t _Query__handle = {
  rosidl_typesupport_fastrtps_cpp::typesupport_identifier,
  &_Query__callbacks,
  get_message_typesupport_handle_function,
  &om_msgs__msg__Query__get_type_hash,
  &om_msgs__msg__Query__get_type_description,
  &om_msgs__msg__Query__get_type_description_sources,
};

}  // namespace typesupport_fastrtps_cpp

}  // namespace msg

}  // namespace om_msgs

namespace rosidl_typesupport_fastrtps_cpp
{

template<>
ROSIDL_TYPESUPPORT_FASTRTPS_CPP_EXPORT_om_msgs
const rosidl_message_type_support_t *
get_message_type_support_handle<om_msgs::msg::Query>()
{
  return &om_msgs::msg::typesupport_fastrtps_cpp::_Query__handle;
}

}  // namespace rosidl_typesupport_fastrtps_cpp

#ifdef __cplusplus
extern "C"
{
#endif

const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_fastrtps_cpp, om_msgs, msg, Query)() {
  return &om_msgs::msg::typesupport_fastrtps_cpp::_Query__handle;
}

#ifdef __cplusplus
}
#endif
