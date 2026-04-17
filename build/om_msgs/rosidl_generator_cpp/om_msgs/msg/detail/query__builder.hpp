// generated from rosidl_generator_cpp/resource/idl__builder.hpp.em
// with input from om_msgs:msg/Query.idl
// generated code does not contain a copyright notice

// IWYU pragma: private, include "om_msgs/msg/query.hpp"


#ifndef OM_MSGS__MSG__DETAIL__QUERY__BUILDER_HPP_
#define OM_MSGS__MSG__DETAIL__QUERY__BUILDER_HPP_

#include <algorithm>
#include <utility>

#include "om_msgs/msg/detail/query__struct.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


namespace om_msgs
{

namespace msg
{

namespace builder
{

class Init_Query_data
{
public:
  explicit Init_Query_data(::om_msgs::msg::Query & msg)
  : msg_(msg)
  {}
  ::om_msgs::msg::Query data(::om_msgs::msg::Query::_data_type arg)
  {
    msg_.data = std::move(arg);
    return std::move(msg_);
  }

private:
  ::om_msgs::msg::Query msg_;
};

class Init_Query_read_num
{
public:
  explicit Init_Query_read_num(::om_msgs::msg::Query & msg)
  : msg_(msg)
  {}
  Init_Query_data read_num(::om_msgs::msg::Query::_read_num_type arg)
  {
    msg_.read_num = std::move(arg);
    return Init_Query_data(msg_);
  }

private:
  ::om_msgs::msg::Query msg_;
};

class Init_Query_write_num
{
public:
  explicit Init_Query_write_num(::om_msgs::msg::Query & msg)
  : msg_(msg)
  {}
  Init_Query_read_num write_num(::om_msgs::msg::Query::_write_num_type arg)
  {
    msg_.write_num = std::move(arg);
    return Init_Query_read_num(msg_);
  }

private:
  ::om_msgs::msg::Query msg_;
};

class Init_Query_read_addr
{
public:
  explicit Init_Query_read_addr(::om_msgs::msg::Query & msg)
  : msg_(msg)
  {}
  Init_Query_write_num read_addr(::om_msgs::msg::Query::_read_addr_type arg)
  {
    msg_.read_addr = std::move(arg);
    return Init_Query_write_num(msg_);
  }

private:
  ::om_msgs::msg::Query msg_;
};

class Init_Query_write_addr
{
public:
  explicit Init_Query_write_addr(::om_msgs::msg::Query & msg)
  : msg_(msg)
  {}
  Init_Query_read_addr write_addr(::om_msgs::msg::Query::_write_addr_type arg)
  {
    msg_.write_addr = std::move(arg);
    return Init_Query_read_addr(msg_);
  }

private:
  ::om_msgs::msg::Query msg_;
};

class Init_Query_func_code
{
public:
  explicit Init_Query_func_code(::om_msgs::msg::Query & msg)
  : msg_(msg)
  {}
  Init_Query_write_addr func_code(::om_msgs::msg::Query::_func_code_type arg)
  {
    msg_.func_code = std::move(arg);
    return Init_Query_write_addr(msg_);
  }

private:
  ::om_msgs::msg::Query msg_;
};

class Init_Query_slave_id
{
public:
  Init_Query_slave_id()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_Query_func_code slave_id(::om_msgs::msg::Query::_slave_id_type arg)
  {
    msg_.slave_id = std::move(arg);
    return Init_Query_func_code(msg_);
  }

private:
  ::om_msgs::msg::Query msg_;
};

}  // namespace builder

}  // namespace msg

template<typename MessageType>
auto build();

template<>
inline
auto build<::om_msgs::msg::Query>()
{
  return om_msgs::msg::builder::Init_Query_slave_id();
}

}  // namespace om_msgs

#endif  // OM_MSGS__MSG__DETAIL__QUERY__BUILDER_HPP_
