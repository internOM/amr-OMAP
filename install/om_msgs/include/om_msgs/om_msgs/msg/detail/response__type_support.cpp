// generated from rosidl_typesupport_introspection_cpp/resource/idl__type_support.cpp.em
// with input from om_msgs:msg/Response.idl
// generated code does not contain a copyright notice

#include "array"
#include "cstddef"
#include "string"
#include "vector"
#include "rosidl_runtime_c/message_type_support_struct.h"
#include "rosidl_typesupport_cpp/message_type_support.hpp"
#include "rosidl_typesupport_interface/macros.h"
#include "om_msgs/msg/detail/response__functions.h"
#include "om_msgs/msg/detail/response__struct.hpp"
#include "rosidl_typesupport_introspection_cpp/field_types.hpp"
#include "rosidl_typesupport_introspection_cpp/identifier.hpp"
#include "rosidl_typesupport_introspection_cpp/message_introspection.hpp"
#include "rosidl_typesupport_introspection_cpp/message_type_support_decl.hpp"
#include "rosidl_typesupport_introspection_cpp/visibility_control.h"

namespace om_msgs
{

namespace msg
{

namespace rosidl_typesupport_introspection_cpp
{

void Response_init_function(
  void * message_memory, rosidl_runtime_cpp::MessageInitialization _init)
{
  new (message_memory) om_msgs::msg::Response(_init);
}

void Response_fini_function(void * message_memory)
{
  auto typed_message = static_cast<om_msgs::msg::Response *>(message_memory);
  typed_message->~Response();
}

size_t size_function__Response__data(const void * untyped_member)
{
  (void)untyped_member;
  return 64;
}

const void * get_const_function__Response__data(const void * untyped_member, size_t index)
{
  const auto & member =
    *reinterpret_cast<const std::array<int32_t, 64> *>(untyped_member);
  return &member[index];
}

void * get_function__Response__data(void * untyped_member, size_t index)
{
  auto & member =
    *reinterpret_cast<std::array<int32_t, 64> *>(untyped_member);
  return &member[index];
}

void fetch_function__Response__data(
  const void * untyped_member, size_t index, void * untyped_value)
{
  const auto & item = *reinterpret_cast<const int32_t *>(
    get_const_function__Response__data(untyped_member, index));
  auto & value = *reinterpret_cast<int32_t *>(untyped_value);
  value = item;
}

void assign_function__Response__data(
  void * untyped_member, size_t index, const void * untyped_value)
{
  auto & item = *reinterpret_cast<int32_t *>(
    get_function__Response__data(untyped_member, index));
  const auto & value = *reinterpret_cast<const int32_t *>(untyped_value);
  item = value;
}

static const ::rosidl_typesupport_introspection_cpp::MessageMember Response_message_member_array[3] = {
  {
    "data",  // name
    ::rosidl_typesupport_introspection_cpp::ROS_TYPE_INT32,  // type
    0,  // upper bound of string
    nullptr,  // members of sub message
    false,  // is key
    true,  // is array
    64,  // array size
    false,  // is upper bound
    offsetof(om_msgs::msg::Response, data),  // bytes offset in struct
    nullptr,  // default value
    size_function__Response__data,  // size() function pointer
    get_const_function__Response__data,  // get_const(index) function pointer
    get_function__Response__data,  // get(index) function pointer
    fetch_function__Response__data,  // fetch(index, &value) function pointer
    assign_function__Response__data,  // assign(index, value) function pointer
    nullptr  // resize(index) function pointer
  },
  {
    "slave_id",  // name
    ::rosidl_typesupport_introspection_cpp::ROS_TYPE_INT8,  // type
    0,  // upper bound of string
    nullptr,  // members of sub message
    false,  // is key
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(om_msgs::msg::Response, slave_id),  // bytes offset in struct
    nullptr,  // default value
    nullptr,  // size() function pointer
    nullptr,  // get_const(index) function pointer
    nullptr,  // get(index) function pointer
    nullptr,  // fetch(index, &value) function pointer
    nullptr,  // assign(index, value) function pointer
    nullptr  // resize(index) function pointer
  },
  {
    "func_code",  // name
    ::rosidl_typesupport_introspection_cpp::ROS_TYPE_INT8,  // type
    0,  // upper bound of string
    nullptr,  // members of sub message
    false,  // is key
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(om_msgs::msg::Response, func_code),  // bytes offset in struct
    nullptr,  // default value
    nullptr,  // size() function pointer
    nullptr,  // get_const(index) function pointer
    nullptr,  // get(index) function pointer
    nullptr,  // fetch(index, &value) function pointer
    nullptr,  // assign(index, value) function pointer
    nullptr  // resize(index) function pointer
  }
};

static const ::rosidl_typesupport_introspection_cpp::MessageMembers Response_message_members = {
  "om_msgs::msg",  // message namespace
  "Response",  // message name
  3,  // number of fields
  sizeof(om_msgs::msg::Response),
  false,  // has_any_key_member_
  Response_message_member_array,  // message members
  Response_init_function,  // function to initialize message memory (memory has to be allocated)
  Response_fini_function  // function to terminate message instance (will not free memory)
};

static const rosidl_message_type_support_t Response_message_type_support_handle = {
  ::rosidl_typesupport_introspection_cpp::typesupport_identifier,
  &Response_message_members,
  get_message_typesupport_handle_function,
  &om_msgs__msg__Response__get_type_hash,
  &om_msgs__msg__Response__get_type_description,
  &om_msgs__msg__Response__get_type_description_sources,
};

}  // namespace rosidl_typesupport_introspection_cpp

}  // namespace msg

}  // namespace om_msgs


namespace rosidl_typesupport_introspection_cpp
{

template<>
ROSIDL_TYPESUPPORT_INTROSPECTION_CPP_PUBLIC
const rosidl_message_type_support_t *
get_message_type_support_handle<om_msgs::msg::Response>()
{
  return &::om_msgs::msg::rosidl_typesupport_introspection_cpp::Response_message_type_support_handle;
}

}  // namespace rosidl_typesupport_introspection_cpp

#ifdef __cplusplus
extern "C"
{
#endif

ROSIDL_TYPESUPPORT_INTROSPECTION_CPP_PUBLIC
const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_cpp, om_msgs, msg, Response)() {
  return &::om_msgs::msg::rosidl_typesupport_introspection_cpp::Response_message_type_support_handle;
}

#ifdef __cplusplus
}
#endif
