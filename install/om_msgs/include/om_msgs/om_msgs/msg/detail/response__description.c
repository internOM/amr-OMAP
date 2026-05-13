// generated from rosidl_generator_c/resource/idl__description.c.em
// with input from om_msgs:msg/Response.idl
// generated code does not contain a copyright notice

#include "om_msgs/msg/detail/response__functions.h"

ROSIDL_GENERATOR_C_PUBLIC_om_msgs
const rosidl_type_hash_t *
om_msgs__msg__Response__get_type_hash(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static rosidl_type_hash_t hash = {1, {
      0x6c, 0x11, 0x3f, 0xa5, 0xec, 0x5f, 0x92, 0xe3,
      0x09, 0xce, 0x5d, 0xe0, 0x29, 0x8d, 0x05, 0x66,
      0xe0, 0x59, 0xfc, 0x86, 0xf6, 0x9f, 0x0b, 0x99,
      0x6c, 0xea, 0xa1, 0xd1, 0x8a, 0x5f, 0x73, 0x86,
    }};
  return &hash;
}

#include <assert.h>
#include <string.h>

// Include directives for referenced types

// Hashes for external referenced types
#ifndef NDEBUG
#endif

static char om_msgs__msg__Response__TYPE_NAME[] = "om_msgs/msg/Response";

// Define type names, field names, and default values
static char om_msgs__msg__Response__FIELD_NAME__data[] = "data";
static char om_msgs__msg__Response__FIELD_NAME__slave_id[] = "slave_id";
static char om_msgs__msg__Response__FIELD_NAME__func_code[] = "func_code";

static rosidl_runtime_c__type_description__Field om_msgs__msg__Response__FIELDS[] = {
  {
    {om_msgs__msg__Response__FIELD_NAME__data, 4, 4},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_INT32_ARRAY,
      64,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {om_msgs__msg__Response__FIELD_NAME__slave_id, 8, 8},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_INT8,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {om_msgs__msg__Response__FIELD_NAME__func_code, 9, 9},
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
om_msgs__msg__Response__get_type_description(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static bool constructed = false;
  static const rosidl_runtime_c__type_description__TypeDescription description = {
    {
      {om_msgs__msg__Response__TYPE_NAME, 20, 20},
      {om_msgs__msg__Response__FIELDS, 3, 3},
    },
    {NULL, 0, 0},
  };
  if (!constructed) {
    constructed = true;
  }
  return &description;
}

static char toplevel_type_raw_source[] =
  "int32[64] data\n"
  "int8 slave_id\n"
  "int8 func_code\n"
  "";

static char msg_encoding[] = "msg";

// Define all individual source functions

const rosidl_runtime_c__type_description__TypeSource *
om_msgs__msg__Response__get_individual_type_description_source(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static const rosidl_runtime_c__type_description__TypeSource source = {
    {om_msgs__msg__Response__TYPE_NAME, 20, 20},
    {msg_encoding, 3, 3},
    {toplevel_type_raw_source, 45, 45},
  };
  return &source;
}

const rosidl_runtime_c__type_description__TypeSource__Sequence *
om_msgs__msg__Response__get_type_description_sources(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static rosidl_runtime_c__type_description__TypeSource sources[1];
  static const rosidl_runtime_c__type_description__TypeSource__Sequence source_sequence = {sources, 1, 1};
  static bool constructed = false;
  if (!constructed) {
    sources[0] = *om_msgs__msg__Response__get_individual_type_description_source(NULL),
    constructed = true;
  }
  return &source_sequence;
}
