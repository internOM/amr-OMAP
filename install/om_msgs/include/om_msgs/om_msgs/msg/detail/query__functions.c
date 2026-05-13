// generated from rosidl_generator_c/resource/idl__functions.c.em
// with input from om_msgs:msg/Query.idl
// generated code does not contain a copyright notice
#include "om_msgs/msg/detail/query__functions.h"

#include <assert.h>
#include <stdbool.h>
#include <stdlib.h>
#include <string.h>

#include "rcutils/allocator.h"


bool
om_msgs__msg__Query__init(om_msgs__msg__Query * msg)
{
  if (!msg) {
    return false;
  }
  // slave_id
  // func_code
  // write_addr
  // read_addr
  // write_num
  // read_num
  // data
  return true;
}

void
om_msgs__msg__Query__fini(om_msgs__msg__Query * msg)
{
  if (!msg) {
    return;
  }
  // slave_id
  // func_code
  // write_addr
  // read_addr
  // write_num
  // read_num
  // data
}

bool
om_msgs__msg__Query__are_equal(const om_msgs__msg__Query * lhs, const om_msgs__msg__Query * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  // slave_id
  if (lhs->slave_id != rhs->slave_id) {
    return false;
  }
  // func_code
  if (lhs->func_code != rhs->func_code) {
    return false;
  }
  // write_addr
  if (lhs->write_addr != rhs->write_addr) {
    return false;
  }
  // read_addr
  if (lhs->read_addr != rhs->read_addr) {
    return false;
  }
  // write_num
  if (lhs->write_num != rhs->write_num) {
    return false;
  }
  // read_num
  if (lhs->read_num != rhs->read_num) {
    return false;
  }
  // data
  for (size_t i = 0; i < 64; ++i) {
    if (lhs->data[i] != rhs->data[i]) {
      return false;
    }
  }
  return true;
}

bool
om_msgs__msg__Query__copy(
  const om_msgs__msg__Query * input,
  om_msgs__msg__Query * output)
{
  if (!input || !output) {
    return false;
  }
  // slave_id
  output->slave_id = input->slave_id;
  // func_code
  output->func_code = input->func_code;
  // write_addr
  output->write_addr = input->write_addr;
  // read_addr
  output->read_addr = input->read_addr;
  // write_num
  output->write_num = input->write_num;
  // read_num
  output->read_num = input->read_num;
  // data
  for (size_t i = 0; i < 64; ++i) {
    output->data[i] = input->data[i];
  }
  return true;
}

om_msgs__msg__Query *
om_msgs__msg__Query__create(void)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  om_msgs__msg__Query * msg = (om_msgs__msg__Query *)allocator.allocate(sizeof(om_msgs__msg__Query), allocator.state);
  if (!msg) {
    return NULL;
  }
  memset(msg, 0, sizeof(om_msgs__msg__Query));
  bool success = om_msgs__msg__Query__init(msg);
  if (!success) {
    allocator.deallocate(msg, allocator.state);
    return NULL;
  }
  return msg;
}

void
om_msgs__msg__Query__destroy(om_msgs__msg__Query * msg)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (msg) {
    om_msgs__msg__Query__fini(msg);
  }
  allocator.deallocate(msg, allocator.state);
}


bool
om_msgs__msg__Query__Sequence__init(om_msgs__msg__Query__Sequence * array, size_t size)
{
  if (!array) {
    return false;
  }
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  om_msgs__msg__Query * data = NULL;

  if (size) {
    data = (om_msgs__msg__Query *)allocator.zero_allocate(size, sizeof(om_msgs__msg__Query), allocator.state);
    if (!data) {
      return false;
    }
    // initialize all array elements
    size_t i;
    for (i = 0; i < size; ++i) {
      bool success = om_msgs__msg__Query__init(&data[i]);
      if (!success) {
        break;
      }
    }
    if (i < size) {
      // if initialization failed finalize the already initialized array elements
      for (; i > 0; --i) {
        om_msgs__msg__Query__fini(&data[i - 1]);
      }
      allocator.deallocate(data, allocator.state);
      return false;
    }
  }
  array->data = data;
  array->size = size;
  array->capacity = size;
  return true;
}

void
om_msgs__msg__Query__Sequence__fini(om_msgs__msg__Query__Sequence * array)
{
  if (!array) {
    return;
  }
  rcutils_allocator_t allocator = rcutils_get_default_allocator();

  if (array->data) {
    // ensure that data and capacity values are consistent
    assert(array->capacity > 0);
    // finalize all array elements
    for (size_t i = 0; i < array->capacity; ++i) {
      om_msgs__msg__Query__fini(&array->data[i]);
    }
    allocator.deallocate(array->data, allocator.state);
    array->data = NULL;
    array->size = 0;
    array->capacity = 0;
  } else {
    // ensure that data, size, and capacity values are consistent
    assert(0 == array->size);
    assert(0 == array->capacity);
  }
}

om_msgs__msg__Query__Sequence *
om_msgs__msg__Query__Sequence__create(size_t size)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  om_msgs__msg__Query__Sequence * array = (om_msgs__msg__Query__Sequence *)allocator.allocate(sizeof(om_msgs__msg__Query__Sequence), allocator.state);
  if (!array) {
    return NULL;
  }
  bool success = om_msgs__msg__Query__Sequence__init(array, size);
  if (!success) {
    allocator.deallocate(array, allocator.state);
    return NULL;
  }
  return array;
}

void
om_msgs__msg__Query__Sequence__destroy(om_msgs__msg__Query__Sequence * array)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (array) {
    om_msgs__msg__Query__Sequence__fini(array);
  }
  allocator.deallocate(array, allocator.state);
}

bool
om_msgs__msg__Query__Sequence__are_equal(const om_msgs__msg__Query__Sequence * lhs, const om_msgs__msg__Query__Sequence * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  if (lhs->size != rhs->size) {
    return false;
  }
  for (size_t i = 0; i < lhs->size; ++i) {
    if (!om_msgs__msg__Query__are_equal(&(lhs->data[i]), &(rhs->data[i]))) {
      return false;
    }
  }
  return true;
}

bool
om_msgs__msg__Query__Sequence__copy(
  const om_msgs__msg__Query__Sequence * input,
  om_msgs__msg__Query__Sequence * output)
{
  if (!input || !output) {
    return false;
  }
  if (output->capacity < input->size) {
    const size_t allocation_size =
      input->size * sizeof(om_msgs__msg__Query);
    rcutils_allocator_t allocator = rcutils_get_default_allocator();
    om_msgs__msg__Query * data =
      (om_msgs__msg__Query *)allocator.reallocate(
      output->data, allocation_size, allocator.state);
    if (!data) {
      return false;
    }
    // If reallocation succeeded, memory may or may not have been moved
    // to fulfill the allocation request, invalidating output->data.
    output->data = data;
    for (size_t i = output->capacity; i < input->size; ++i) {
      if (!om_msgs__msg__Query__init(&output->data[i])) {
        // If initialization of any new item fails, roll back
        // all previously initialized items. Existing items
        // in output are to be left unmodified.
        for (; i-- > output->capacity; ) {
          om_msgs__msg__Query__fini(&output->data[i]);
        }
        return false;
      }
    }
    output->capacity = input->size;
  }
  output->size = input->size;
  for (size_t i = 0; i < input->size; ++i) {
    if (!om_msgs__msg__Query__copy(
        &(input->data[i]), &(output->data[i])))
    {
      return false;
    }
  }
  return true;
}
