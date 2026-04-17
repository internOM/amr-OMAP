// generated from rosidl_generator_cpp/resource/idl__struct.hpp.em
// with input from om_msgs:msg/Query.idl
// generated code does not contain a copyright notice

// IWYU pragma: private, include "om_msgs/msg/query.hpp"


#ifndef OM_MSGS__MSG__DETAIL__QUERY__STRUCT_HPP_
#define OM_MSGS__MSG__DETAIL__QUERY__STRUCT_HPP_

#include <algorithm>
#include <array>
#include <cstdint>
#include <memory>
#include <string>
#include <vector>

#include "rosidl_runtime_cpp/bounded_vector.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


#ifndef _WIN32
# define DEPRECATED__om_msgs__msg__Query __attribute__((deprecated))
#else
# define DEPRECATED__om_msgs__msg__Query __declspec(deprecated)
#endif

namespace om_msgs
{

namespace msg
{

// message struct
template<class ContainerAllocator>
struct Query_
{
  using Type = Query_<ContainerAllocator>;

  explicit Query_(rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->slave_id = 0;
      this->func_code = 0;
      this->write_addr = 0l;
      this->read_addr = 0l;
      this->write_num = 0;
      this->read_num = 0;
      std::fill<typename std::array<int32_t, 64>::iterator, int32_t>(this->data.begin(), this->data.end(), 0l);
    }
  }

  explicit Query_(const ContainerAllocator & _alloc, rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  : data(_alloc)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->slave_id = 0;
      this->func_code = 0;
      this->write_addr = 0l;
      this->read_addr = 0l;
      this->write_num = 0;
      this->read_num = 0;
      std::fill<typename std::array<int32_t, 64>::iterator, int32_t>(this->data.begin(), this->data.end(), 0l);
    }
  }

  // field types and members
  using _slave_id_type =
    int8_t;
  _slave_id_type slave_id;
  using _func_code_type =
    int8_t;
  _func_code_type func_code;
  using _write_addr_type =
    int32_t;
  _write_addr_type write_addr;
  using _read_addr_type =
    int32_t;
  _read_addr_type read_addr;
  using _write_num_type =
    int8_t;
  _write_num_type write_num;
  using _read_num_type =
    int8_t;
  _read_num_type read_num;
  using _data_type =
    std::array<int32_t, 64>;
  _data_type data;

  // setters for named parameter idiom
  Type & set__slave_id(
    const int8_t & _arg)
  {
    this->slave_id = _arg;
    return *this;
  }
  Type & set__func_code(
    const int8_t & _arg)
  {
    this->func_code = _arg;
    return *this;
  }
  Type & set__write_addr(
    const int32_t & _arg)
  {
    this->write_addr = _arg;
    return *this;
  }
  Type & set__read_addr(
    const int32_t & _arg)
  {
    this->read_addr = _arg;
    return *this;
  }
  Type & set__write_num(
    const int8_t & _arg)
  {
    this->write_num = _arg;
    return *this;
  }
  Type & set__read_num(
    const int8_t & _arg)
  {
    this->read_num = _arg;
    return *this;
  }
  Type & set__data(
    const std::array<int32_t, 64> & _arg)
  {
    this->data = _arg;
    return *this;
  }

  // constant declarations

  // pointer types
  using RawPtr =
    om_msgs::msg::Query_<ContainerAllocator> *;
  using ConstRawPtr =
    const om_msgs::msg::Query_<ContainerAllocator> *;
  using SharedPtr =
    std::shared_ptr<om_msgs::msg::Query_<ContainerAllocator>>;
  using ConstSharedPtr =
    std::shared_ptr<om_msgs::msg::Query_<ContainerAllocator> const>;

  template<typename Deleter = std::default_delete<
      om_msgs::msg::Query_<ContainerAllocator>>>
  using UniquePtrWithDeleter =
    std::unique_ptr<om_msgs::msg::Query_<ContainerAllocator>, Deleter>;

  using UniquePtr = UniquePtrWithDeleter<>;

  template<typename Deleter = std::default_delete<
      om_msgs::msg::Query_<ContainerAllocator>>>
  using ConstUniquePtrWithDeleter =
    std::unique_ptr<om_msgs::msg::Query_<ContainerAllocator> const, Deleter>;
  using ConstUniquePtr = ConstUniquePtrWithDeleter<>;

  using WeakPtr =
    std::weak_ptr<om_msgs::msg::Query_<ContainerAllocator>>;
  using ConstWeakPtr =
    std::weak_ptr<om_msgs::msg::Query_<ContainerAllocator> const>;

  // pointer types similar to ROS 1, use SharedPtr / ConstSharedPtr instead
  // NOTE: Can't use 'using' here because GNU C++ can't parse attributes properly
  typedef DEPRECATED__om_msgs__msg__Query
    std::shared_ptr<om_msgs::msg::Query_<ContainerAllocator>>
    Ptr;
  typedef DEPRECATED__om_msgs__msg__Query
    std::shared_ptr<om_msgs::msg::Query_<ContainerAllocator> const>
    ConstPtr;

  // comparison operators
  bool operator==(const Query_ & other) const
  {
    if (this->slave_id != other.slave_id) {
      return false;
    }
    if (this->func_code != other.func_code) {
      return false;
    }
    if (this->write_addr != other.write_addr) {
      return false;
    }
    if (this->read_addr != other.read_addr) {
      return false;
    }
    if (this->write_num != other.write_num) {
      return false;
    }
    if (this->read_num != other.read_num) {
      return false;
    }
    if (this->data != other.data) {
      return false;
    }
    return true;
  }
  bool operator!=(const Query_ & other) const
  {
    return !this->operator==(other);
  }
};  // struct Query_

// alias to use template instance with default allocator
using Query =
  om_msgs::msg::Query_<std::allocator<void>>;

// constant definitions

}  // namespace msg

}  // namespace om_msgs

#endif  // OM_MSGS__MSG__DETAIL__QUERY__STRUCT_HPP_
