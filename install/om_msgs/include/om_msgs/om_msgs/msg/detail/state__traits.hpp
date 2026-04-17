// generated from rosidl_generator_cpp/resource/idl__traits.hpp.em
// with input from om_msgs:msg/State.idl
// generated code does not contain a copyright notice

// IWYU pragma: private, include "om_msgs/msg/state.hpp"


#ifndef OM_MSGS__MSG__DETAIL__STATE__TRAITS_HPP_
#define OM_MSGS__MSG__DETAIL__STATE__TRAITS_HPP_

#include <stdint.h>

#include <sstream>
#include <string>
#include <type_traits>

#include "om_msgs/msg/detail/state__struct.hpp"
#include "rosidl_runtime_cpp/traits.hpp"

namespace om_msgs
{

namespace msg
{

inline void to_flow_style_yaml(
  const State & msg,
  std::ostream & out)
{
  out << "{";
  // member: state_driver
  {
    out << "state_driver: ";
    rosidl_generator_traits::value_to_yaml(msg.state_driver, out);
    out << ", ";
  }

  // member: state_mes
  {
    out << "state_mes: ";
    rosidl_generator_traits::value_to_yaml(msg.state_mes, out);
    out << ", ";
  }

  // member: state_error
  {
    out << "state_error: ";
    rosidl_generator_traits::value_to_yaml(msg.state_error, out);
  }
  out << "}";
}  // NOLINT(readability/fn_size)

inline void to_block_style_yaml(
  const State & msg,
  std::ostream & out, size_t indentation = 0)
{
  // member: state_driver
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "state_driver: ";
    rosidl_generator_traits::value_to_yaml(msg.state_driver, out);
    out << "\n";
  }

  // member: state_mes
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "state_mes: ";
    rosidl_generator_traits::value_to_yaml(msg.state_mes, out);
    out << "\n";
  }

  // member: state_error
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "state_error: ";
    rosidl_generator_traits::value_to_yaml(msg.state_error, out);
    out << "\n";
  }
}  // NOLINT(readability/fn_size)

inline std::string to_yaml(const State & msg, bool use_flow_style = false)
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
  const om_msgs::msg::State & msg,
  std::ostream & out, size_t indentation = 0)
{
  om_msgs::msg::to_block_style_yaml(msg, out, indentation);
}

[[deprecated("use om_msgs::msg::to_yaml() instead")]]
inline std::string to_yaml(const om_msgs::msg::State & msg)
{
  return om_msgs::msg::to_yaml(msg);
}

template<>
inline const char * data_type<om_msgs::msg::State>()
{
  return "om_msgs::msg::State";
}

template<>
inline const char * name<om_msgs::msg::State>()
{
  return "om_msgs/msg/State";
}

template<>
struct has_fixed_size<om_msgs::msg::State>
  : std::integral_constant<bool, true> {};

template<>
struct has_bounded_size<om_msgs::msg::State>
  : std::integral_constant<bool, true> {};

template<>
struct is_message<om_msgs::msg::State>
  : std::true_type {};

}  // namespace rosidl_generator_traits

#endif  // OM_MSGS__MSG__DETAIL__STATE__TRAITS_HPP_
