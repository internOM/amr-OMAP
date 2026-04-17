// generated from rosidl_generator_cpp/resource/idl__struct.hpp.em
// with input from om_msgs:msg/State.idl
// generated code does not contain a copyright notice

// IWYU pragma: private, include "om_msgs/msg/state.hpp"


#ifndef OM_MSGS__MSG__DETAIL__STATE__STRUCT_HPP_
#define OM_MSGS__MSG__DETAIL__STATE__STRUCT_HPP_

#include <algorithm>
#include <array>
#include <cstdint>
#include <memory>
#include <string>
#include <vector>

#include "rosidl_runtime_cpp/bounded_vector.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


#ifndef _WIN32
# define DEPRECATED__om_msgs__msg__State __attribute__((deprecated))
#else
# define DEPRECATED__om_msgs__msg__State __declspec(deprecated)
#endif

namespace om_msgs
{

namespace msg
{

// message struct
template<class ContainerAllocator>
struct State_
{
  using Type = State_<ContainerAllocator>;

  explicit State_(rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->state_driver = 0;
      this->state_mes = 0;
      this->state_error = 0;
    }
  }

  explicit State_(const ContainerAllocator & _alloc, rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  {
    (void)_alloc;
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->state_driver = 0;
      this->state_mes = 0;
      this->state_error = 0;
    }
  }

  // field types and members
  using _state_driver_type =
    int8_t;
  _state_driver_type state_driver;
  using _state_mes_type =
    int8_t;
  _state_mes_type state_mes;
  using _state_error_type =
    int8_t;
  _state_error_type state_error;

  // setters for named parameter idiom
  Type & set__state_driver(
    const int8_t & _arg)
  {
    this->state_driver = _arg;
    return *this;
  }
  Type & set__state_mes(
    const int8_t & _arg)
  {
    this->state_mes = _arg;
    return *this;
  }
  Type & set__state_error(
    const int8_t & _arg)
  {
    this->state_error = _arg;
    return *this;
  }

  // constant declarations

  // pointer types
  using RawPtr =
    om_msgs::msg::State_<ContainerAllocator> *;
  using ConstRawPtr =
    const om_msgs::msg::State_<ContainerAllocator> *;
  using SharedPtr =
    std::shared_ptr<om_msgs::msg::State_<ContainerAllocator>>;
  using ConstSharedPtr =
    std::shared_ptr<om_msgs::msg::State_<ContainerAllocator> const>;

  template<typename Deleter = std::default_delete<
      om_msgs::msg::State_<ContainerAllocator>>>
  using UniquePtrWithDeleter =
    std::unique_ptr<om_msgs::msg::State_<ContainerAllocator>, Deleter>;

  using UniquePtr = UniquePtrWithDeleter<>;

  template<typename Deleter = std::default_delete<
      om_msgs::msg::State_<ContainerAllocator>>>
  using ConstUniquePtrWithDeleter =
    std::unique_ptr<om_msgs::msg::State_<ContainerAllocator> const, Deleter>;
  using ConstUniquePtr = ConstUniquePtrWithDeleter<>;

  using WeakPtr =
    std::weak_ptr<om_msgs::msg::State_<ContainerAllocator>>;
  using ConstWeakPtr =
    std::weak_ptr<om_msgs::msg::State_<ContainerAllocator> const>;

  // pointer types similar to ROS 1, use SharedPtr / ConstSharedPtr instead
  // NOTE: Can't use 'using' here because GNU C++ can't parse attributes properly
  typedef DEPRECATED__om_msgs__msg__State
    std::shared_ptr<om_msgs::msg::State_<ContainerAllocator>>
    Ptr;
  typedef DEPRECATED__om_msgs__msg__State
    std::shared_ptr<om_msgs::msg::State_<ContainerAllocator> const>
    ConstPtr;

  // comparison operators
  bool operator==(const State_ & other) const
  {
    if (this->state_driver != other.state_driver) {
      return false;
    }
    if (this->state_mes != other.state_mes) {
      return false;
    }
    if (this->state_error != other.state_error) {
      return false;
    }
    return true;
  }
  bool operator!=(const State_ & other) const
  {
    return !this->operator==(other);
  }
};  // struct State_

// alias to use template instance with default allocator
using State =
  om_msgs::msg::State_<std::allocator<void>>;

// constant definitions

}  // namespace msg

}  // namespace om_msgs

#endif  // OM_MSGS__MSG__DETAIL__STATE__STRUCT_HPP_
