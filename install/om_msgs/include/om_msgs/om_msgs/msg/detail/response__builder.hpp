// generated from rosidl_generator_cpp/resource/idl__builder.hpp.em
// with input from om_msgs:msg/Response.idl
// generated code does not contain a copyright notice

// IWYU pragma: private, include "om_msgs/msg/response.hpp"


#ifndef OM_MSGS__MSG__DETAIL__RESPONSE__BUILDER_HPP_
#define OM_MSGS__MSG__DETAIL__RESPONSE__BUILDER_HPP_

#include <algorithm>
#include <utility>

#include "om_msgs/msg/detail/response__struct.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


namespace om_msgs
{

namespace msg
{

namespace builder
{

class Init_Response_func_code
{
public:
  explicit Init_Response_func_code(::om_msgs::msg::Response & msg)
  : msg_(msg)
  {}
  ::om_msgs::msg::Response func_code(::om_msgs::msg::Response::_func_code_type arg)
  {
    msg_.func_code = std::move(arg);
    return std::move(msg_);
  }

private:
  ::om_msgs::msg::Response msg_;
};

class Init_Response_slave_id
{
public:
  explicit Init_Response_slave_id(::om_msgs::msg::Response & msg)
  : msg_(msg)
  {}
  Init_Response_func_code slave_id(::om_msgs::msg::Response::_slave_id_type arg)
  {
    msg_.slave_id = std::move(arg);
    return Init_Response_func_code(msg_);
  }

private:
  ::om_msgs::msg::Response msg_;
};

class Init_Response_data
{
public:
  Init_Response_data()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_Response_slave_id data(::om_msgs::msg::Response::_data_type arg)
  {
    msg_.data = std::move(arg);
    return Init_Response_slave_id(msg_);
  }

private:
  ::om_msgs::msg::Response msg_;
};

}  // namespace builder

}  // namespace msg

template<typename MessageType>
auto build();

template<>
inline
auto build<::om_msgs::msg::Response>()
{
  return om_msgs::msg::builder::Init_Response_data();
}

}  // namespace om_msgs

#endif  // OM_MSGS__MSG__DETAIL__RESPONSE__BUILDER_HPP_
