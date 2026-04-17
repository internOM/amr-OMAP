// generated from rosidl_generator_c/resource/idl__functions.c.em
// with input from om_msgs:msg/Response.idl
// generated code does not contain a copyright notice
#include "om_msgs/msg/detail/response__functions.h"

#include <assert.h>
#include <stdbool.h>
#include <stdlib.h>
#include <string.h>

#include "rcutils/allocator.h"


bool
om_msgs__msg__Response__init(om_msgs__msg__Response * msg)
{
  if (!msg) {
    return false;
  }
  // data
  // slave_id
  // func_code
  return true;
}

void
om_msgs__msg__Response__fini(om_msgs__msg__Response * msg)
{
  if (!msg) {
    return;
  }
  // data
  // slave_id
  // func_code
}

bool
om_msgs__msg__Response__are_equal(const om_msgs__msg__Response * lhs, const om_msgs__msg__Response * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  // data
  for (size_t i = 0; i < 64; ++i) {
    if (lhs->data[i] != rhs->data[i]) {
      return false;
    }
  }
  // slave_id
  if (lhs->slave_id != rhs->slave_id) {
    return false;
  }
  // func_code
  if (lhs->func_code != rhs->func_code) {
    return false;
  }
  return true;
}

bool
om_msgs__msg__Response__copy(
  const om_msgs__msg__Response * input,
  om_msgs__msg__Response * output)
{
  if (!input || !output) {
    return false;
  }
  // data
  for (size_t i = 0; i < 64; ++i) {
    output->data[i] = input->data[i];
  }
  // slave_id
  output->slave_id = input->slave_id;
  // func_code
  output->func_code = input->func_code;
  return true;
}

om_msgs__msg__Response *
om_msgs__msg__Response__create(void)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  om_msgs__msg__Response * msg = (om_msgs__msg__Response *)allocator.allocate(sizeof(om_msgs__msg__Response), allocator.state);
  if (!msg) {
    return NULL;
  }
  memset(msg, 0, sizeof(om_msgs__msg__Response));
  bool success = om_msgs__msg__Response__init(msg);
  if (!success) {
    allocator.deallocate(msg, allocator.state);
    return NULL;
  }
  return msg;
}

void
om_msgs__msg__Response__destroy(om_msgs__msg__Response * msg)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (msg) {
    om_msgs__msg__Response__fini(msg);
  }
  allocator.deallocate(msg, allocator.state);
}


bool
om_msgs__msg__Response__Sequence__init(om_msgs__msg__Response__Sequence * array, size_t size)
{
  if (!array) {
    return false;
  }
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  om_msgs__msg__Response * data = NULL;

  if (size) {
    data = (om_msgs__msg__Response *)allocator.zero_allocate(size, sizeof(om_msgs__msg__Response), allocator.state);
    if (!data) {
      return false;
    }
    // initialize all array elements
    size_t i;
    for (i = 0; i < size; ++i) {
      bool success = om_msgs__msg__Response__init(&data[i]);
      if (!success) {
        break;
      }
    }
    if (i < size) {
      // if initialization failed finalize the already initialized array elements
      for (; i > 0; --i) {
        om_msgs__msg__Response__fini(&data[i - 1]);
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
om_msgs__msg__Response__Sequence__fini(om_msgs__msg__Response__Sequence * array)
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
      om_msgs__msg__Response__fini(&array->data[i]);
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

om_msgs__msg__Response__Sequence *
om_msgs__msg__Response__Sequence__create(size_t size)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  om_msgs__msg__Response__Sequence * array = (om_msgs__msg__Response__Sequence *)allocator.allocate(sizeof(om_msgs__msg__Response__Sequence), allocator.state);
  if (!array) {
    return NULL;
  }
  bool success = om_msgs__msg__Response__Sequence__init(array, size);
  if (!success) {
    allocator.deallocate(array, allocator.state);
    return NULL;
  }
  return array;
}

void
om_msgs__msg__Response__Sequence__destroy(om_msgs__msg__Response__Sequence * array)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (array) {
    om_msgs__msg__Response__Sequence__fini(array);
  }
  allocator.deallocate(array, allocator.state);
}

bool
om_msgs__msg__Response__Sequence__are_equal(const om_msgs__msg__Response__Sequence * lhs, const om_msgs__msg__Response__Sequence * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  if (lhs->size != rhs->size) {
    return false;
  }
  for (size_t i = 0; i < lhs->size; ++i) {
    if (!om_msgs__msg__Response__are_equal(&(lhs->data[i]), &(rhs->data[i]))) {
      return false;
    }
  }
  return true;
}

bool
om_msgs__msg__Response__Sequence__copy(
  const om_msgs__msg__Response__Sequence * input,
  om_msgs__msg__Response__Sequence * output)
{
  if (!input || !output) {
    return false;
  }
  if (output->capacity < input->size) {
    const size_t allocation_size =
      input->size * sizeof(om_msgs__msg__Response);
    rcutils_allocator_t allocator = rcutils_get_default_allocator();
    om_msgs__msg__Response * data =
      (om_msgs__msg__Response *)allocator.reallocate(
      output->data, allocation_size, allocator.state);
    if (!data) {
      return false;
    }
    // If reallocation succeeded, memory may or may not have been moved
    // to fulfill the allocation request, invalidating output->data.
    output->data = data;
    for (size_t i = output->capacity; i < input->size; ++i) {
      if (!om_msgs__msg__Response__init(&output->data[i])) {
        // If initialization of any new item fails, roll back
        // all previously initialized items. Existing items
        // in output are to be left unmodified.
        for (; i-- > output->capacity; ) {
          om_msgs__msg__Response__fini(&output->data[i]);
        }
        return false;
      }
    }
    output->capacity = input->size;
  }
  output->size = input->size;
  for (size_t i = 0; i < input->size; ++i) {
    if (!om_msgs__msg__Response__copy(
        &(input->data[i]), &(output->data[i])))
    {
      return false;
    }
  }
  return true;
}
