// generated from rosidl_generator_c/resource/idl__description.c.em
// with input from om_msgs:msg/State.idl
// generated code does not contain a copyright notice

#include "om_msgs/msg/detail/state__functions.h"

ROSIDL_GENERATOR_C_PUBLIC_om_msgs
const rosidl_type_hash_t *
om_msgs__msg__State__get_type_hash(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static rosidl_type_hash_t hash = {1, {
      0x07, 0x6d, 0xa8, 0x4e, 0x06, 0x18, 0x3a, 0xcc,
      0x00, 0x83, 0x3e, 0xa6, 0x6e, 0x42, 0xc6, 0x8e,
      0x78, 0x87, 0x49, 0x25, 0x7e, 0xbf, 0x0f, 0xe9,
      0x2f, 0x73, 0x54, 0x37, 0x8a, 0x65, 0xde, 0x7e,
    }};
  return &hash;
}

#include <assert.h>
#include <string.h>

// Include directives for referenced types

// Hashes for external referenced types
#ifndef NDEBUG
#endif

static char om_msgs__msg__State__TYPE_NAME[] = "om_msgs/msg/State";

// Define type names, field names, and default values
static char om_msgs__msg__State__FIELD_NAME__state_driver[] = "state_driver";
static char om_msgs__msg__State__FIELD_NAME__state_mes[] = "state_mes";
static char om_msgs__msg__State__FIELD_NAME__state_error[] = "state_error";

static rosidl_runtime_c__type_description__Field om_msgs__msg__State__FIELDS[] = {
  {
    {om_msgs__msg__State__FIELD_NAME__state_driver, 12, 12},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_INT8,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {om_msgs__msg__State__FIELD_NAME__state_mes, 9, 9},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_INT8,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {om_msgs__msg__State__FIELD_NAME__state_error, 11, 11},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_INT8,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
};

const rosidl_runtime_c__type_description__TypeDescription *
om_msgs__msg__State__get_type_description(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static bool constructed = false;
  static const rosidl_runtime_c__type_description__TypeDescription description = {
    {
      {om_msgs__msg__State__TYPE_NAME, 17, 17},
      {om_msgs__msg__State__FIELDS, 3, 3},
    },
    {NULL, 0, 0},
  };
  if (!constructed) {
    constructed = true;
  }
  return &description;
}

static char toplevel_type_raw_source[] =
  "int8 state_driver\n"
  "int8 state_mes\n"
  "int8 state_error\n"
  "";

static char msg_encoding[] = "msg";

// Define all individual source functions

const rosidl_runtime_c__type_description__TypeSource *
om_msgs__msg__State__get_individual_type_description_source(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static const rosidl_runtime_c__type_description__TypeSource source = {
    {om_msgs__msg__State__TYPE_NAME, 17, 17},
    {msg_encoding, 3, 3},
    {toplevel_type_raw_source, 51, 51},
  };
  return &source;
}

const rosidl_runtime_c__type_description__TypeSource__Sequence *
om_msgs__msg__State__get_type_description_sources(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static rosidl_runtime_c__type_description__TypeSource sources[1];
  static const rosidl_runtime_c__type_description__TypeSource__Sequence source_sequence = {sources, 1, 1};
  static bool constructed = false;
  if (!constructed) {
    sources[0] = *om_msgs__msg__State__get_individual_type_description_source(NULL),
    constructed = true;
  }
  return &source_sequence;
}
