// generated from rosidl_generator_cpp/resource/idl__traits.hpp.em
// with input from om_msgs:msg/Response.idl
// generated code does not contain a copyright notice

// IWYU pragma: private, include "om_msgs/msg/response.hpp"


#ifndef OM_MSGS__MSG__DETAIL__RESPONSE__TRAITS_HPP_
#define OM_MSGS__MSG__DETAIL__RESPONSE__TRAITS_HPP_

#include <stdint.h>

#include <sstream>
#include <string>
#include <type_traits>

#include "om_msgs/msg/detail/response__struct.hpp"
#include "rosidl_runtime_cpp/traits.hpp"

namespace om_msgs
{

namespace msg
{

inline void to_flow_style_yaml(
  const Response & msg,
  std::ostream & out)
{
  out << "{";
  // member: data
  {
    if (msg.data.size() == 0) {
      out << "data: []";
    } else {
      out << "data: [";
      size_t pending_items = msg.data.size();
      for (auto item : msg.data) {
        rosidl_generator_traits::value_to_yaml(item, out);
        if (--pending_items > 0) {
          out << ", ";
        }
      }
      out << "]";
    }
    out << ", ";
  }

  // member: slave_id
  {
    out << "slave_id: ";
    rosidl_generator_traits::value_to_yaml(msg.slave_id, out);
    out << ", ";
  }

  // member: func_code
  {
    out << "func_code: ";
    rosidl_generator_traits::value_to_yaml(msg.func_code, out);
  }
  out << "}";
}  // NOLINT(readability/fn_size)

inline void to_block_style_yaml(
  const Response & msg,
  std::ostream & out, size_t indentation = 0)
{
  // member: data
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    if (msg.data.size() == 0) {
      out << "data: []\n";
    } else {
      out << "data:\n";
      for (auto item : msg.data) {
        if (indentation > 0) {
          out << std::string(indentation, ' ');
        }
        out << "- ";
        rosidl_generator_traits::value_to_yaml(item, out);
        out << "\n";
      }
    }
  }

  // member: slave_id
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "slave_id: ";
    rosidl_generator_traits::value_to_yaml(msg.slave_id, out);
    out << "\n";
  }

  // member: func_code
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "func_code: ";
    rosidl_generator_traits::value_to_yaml(msg.func_code, out);
    out << "\n";
  }
}  // NOLINT(readability/fn_size)

inline std::string to_yaml(const Response & msg, bool use_flow_style = false)
{
  std::ostringstream out;
  if (use_flow_style) {
    to_flow_style_yaml(msg, out);
  } else {
    to_block_style_yaml(msg, out);
  }
  return out.str();
}

}  // namespace msg

}  // namespace om_msgs

namespace rosidl_generator_traits
{

[[deprecated("use om_msgs::msg::to_block_style_yaml() instead")]]
inline void to_yaml(
  const om_msgs::msg::Response & msg,
  std::ostream & out, size_t indentation = 0)
{
  om_msgs::msg::to_block_style_yaml(msg, out, indentation);
}

[[deprecated("use om_msgs::msg::to_yaml() instead")]]
inline std::string to_yaml(const om_msgs::msg::Response & msg)
{
  return om_msgs::msg::to_yaml(msg);
}

template<>
inline const char * data_type<om_msgs::msg::Response>()
{
  return "om_msgs::msg::Response";
}

template<>
inline const char * name<om_msgs::msg::Response>()
{
  return "om_msgs/msg/Response";
}

template<>
struct has_fixed_size<om_msgs::msg::Response>
  : std::integral_constant<bool, true> {};

template<>
struct has_bounded_size<om_msgs::msg::Response>
  : std::integral_constant<bool, true> {};

template<>
struct is_message<om_msgs::msg::Response>
  : std::true_type {};

}  // namespace rosidl_generator_traits

#endif  // OM_MSGS__MSG__DETAIL__RESPONSE__TRAITS_HPP_
