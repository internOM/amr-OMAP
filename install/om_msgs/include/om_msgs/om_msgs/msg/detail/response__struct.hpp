// generated from rosidl_generator_cpp/resource/idl__struct.hpp.em
// with input from om_msgs:msg/Response.idl
// generated code does not contain a copyright notice

// IWYU pragma: private, include "om_msgs/msg/response.hpp"


#ifndef OM_MSGS__MSG__DETAIL__RESPONSE__STRUCT_HPP_
#define OM_MSGS__MSG__DETAIL__RESPONSE__STRUCT_HPP_

#include <algorithm>
#include <array>
#include <cstdint>
#include <memory>
#include <string>
#include <vector>

#include "rosidl_runtime_cpp/bounded_vector.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


#ifndef _WIN32
# define DEPRECATED__om_msgs__msg__Response __attribute__((deprecated))
#else
# define DEPRECATED__om_msgs__msg__Response __declspec(deprecated)
#endif

namespace om_msgs
{

namespace msg
{

// message struct
template<class ContainerAllocator>
struct Response_
{
  using Type = Response_<ContainerAllocator>;

  explicit Response_(rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      std::fill<typename std::array<int32_t, 64>::iterator, int32_t>(this->data.begin(), this->data.end(), 0l);
      this->slave_id = 0;
      this->func_code = 0;
    }
  }

  explicit Response_(const ContainerAllocator & _alloc, rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  : data(_alloc)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      std::fill<typename std::array<int32_t, 64>::iterator, int32_t>(this->data.begin(), this->data.end(), 0l);
      this->slave_id = 0;
      this->func_code = 0;
    }
  }

  // field types and members
  using _data_type =
    std::array<int32_t, 64>;
  _data_type data;
  using _slave_id_type =
    int8_t;
  _slave_id_type slave_id;
  using _func_code_type =
    int8_t;
  _func_code_type func_code;

  // setters for named parameter idiom
  Type & set__data(
    const std::array<int32_t, 64> & _arg)
  {
    this->data = _arg;
    return *this;
  }
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

  // constant declarations

  // pointer types
  using RawPtr =
    om_msgs::msg::Response_<ContainerAllocator> *;
  using ConstRawPtr =
    const om_msgs::msg::Response_<ContainerAllocator> *;
  using SharedPtr =
    std::shared_ptr<om_msgs::msg::Response_<ContainerAllocator>>;
  using ConstSharedPtr =
    std::shared_ptr<om_msgs::msg::Response_<ContainerAllocator> const>;

  template<typename Deleter = std::default_delete<
      om_msgs::msg::Response_<ContainerAllocator>>>
  using UniquePtrWithDeleter =
    std::unique_ptr<om_msgs::msg::Response_<ContainerAllocator>, Deleter>;

  using UniquePtr = UniquePtrWithDeleter<>;

  template<typename Deleter = std::default_delete<
      om_msgs::msg::Response_<ContainerAllocator>>>
  using ConstUniquePtrWithDeleter =
    std::unique_ptr<om_msgs::msg::Response_<ContainerAllocator> const, Deleter>;
  using ConstUniquePtr = ConstUniquePtrWithDeleter<>;

  using WeakPtr =
    std::weak_ptr<om_msgs::msg::Response_<ContainerAllocator>>;
  using ConstWeakPtr =
    std::weak_ptr<om_msgs::msg::Response_<ContainerAllocator> const>;

  // pointer types similar to ROS 1, use SharedPtr / ConstSharedPtr instead
  // NOTE: Can't use 'using' here because GNU C++ can't parse attributes properly
  typedef DEPRECATED__om_msgs__msg__Response
    std::shared_ptr<om_msgs::msg::Response_<ContainerAllocator>>
    Ptr;
  typedef DEPRECATED__om_msgs__msg__Response
    std::shared_ptr<om_msgs::msg::Response_<ContainerAllocator> const>
    ConstPtr;

  // comparison operators
  bool operator==(const Response_ & other) const
  {
    if (this->data != other.data) {
      return false;
    }
    if (this->slave_id != other.slave_id) {
      return false;
    }
    if (this->func_code != other.func_code) {
      return false;
    }
    return true;
  }
  bool operator!=(const Response_ & other) const
  {
    return !this->operator==(other);
  }
};  // struct Response_

// alias to use template instance with default allocator
using Response =
  om_msgs::msg::Response_<std::allocator<void>>;

// constant definitions

}  // namespace msg

}  // namespace om_msgs

#endif  // OM_MSGS__MSG__DETAIL__RESPONSE__STRUCT_HPP_
