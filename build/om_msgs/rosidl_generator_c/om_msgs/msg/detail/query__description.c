// generated from rosidl_generator_c/resource/idl__description.c.em
// with input from om_msgs:msg/Query.idl
// generated code does not contain a copyright notice

#include "om_msgs/msg/detail/query__functions.h"

ROSIDL_GENERATOR_C_PUBLIC_om_msgs
const rosidl_type_hash_t *
om_msgs__msg__Query__get_type_hash(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static rosidl_type_hash_t hash = {1, {
      0x47, 0xf7, 0xa7, 0x8e, 0xc2, 0x46, 0xa9, 0xc9,
      0x54, 0x58, 0x86, 0x6a, 0x31, 0x73, 0x3d, 0xf7,
      0xfb, 0x34, 0xfd, 0xe6, 0x07, 0xe8, 0x51, 0x1b,
      0x7c, 0xb7, 0x0e, 0x46, 0xcd, 0x3c, 0x05, 0x08,
    }};
  return &hash;
}

#include <assert.h>
#include <string.h>

// Include directives for referenced types

// Hashes for external referenced types
#ifndef NDEBUG
#endif

static char om_msgs__msg__Query__TYPE_NAME[] = "om_msgs/msg/Query";

// Define type names, field names, and default values
static char om_msgs__msg__Query__FIELD_NAME__slave_id[] = "slave_id";
static char om_msgs__msg__Query__FIELD_NAME__func_code[] = "func_code";
static char om_msgs__msg__Query__FIELD_NAME__write_addr[] = "write_addr";
static char om_msgs__msg__Query__FIELD_NAME__read_addr[] = "read_addr";
static char om_msgs__msg__Query__FIELD_NAME__write_num[] = "write_num";
static char om_msgs__msg__Query__FIELD_NAME__read_num[] = "read_num";
static char om_msgs__msg__Query__FIELD_NAME__data[] = "data";

static rosidl_runtime_c__type_description__Field om_msgs__msg__Query__FIELDS[] = {
  {
    {om_msgs__msg__Query__FIELD_NAME__slave_id, 8, 8},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_INT8,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {om_msgs__msg__Query__FIELD_NAME__func_code, 9, 9},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_INT8,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {om_msgs__msg__Query__FIELD_NAME__write_addr, 10, 10},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_INT32,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {om_msgs__msg__Query__FIELD_NAME__read_addr, 9, 9},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_INT32,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {om_msgs__msg__Query__FIELD_NAME__write_num, 9, 9},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_INT8,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {om_msgs__msg__Query__FIELD_NAME__read_num, 8, 8},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_INT8,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {om_msgs__msg__Query__FIELD_NAME__data, 4, 4},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_INT32_ARRAY,
      64,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
};

const rosidl_runtime_c__type_description__TypeDescription *
om_msgs__msg__Query__get_type_description(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static bool constructed = false;
  static const rosidl_runtime_c__type_description__TypeDescription description = {
    {
      {om_msgs__msg__Query__TYPE_NAME, 17, 17},
      {om_msgs__msg__Query__FIELDS, 7, 7},
    },
    {NULL, 0, 0},
  };
  if (!constructed) {
    constructed = true;
  }
  return &description;
}

static char toplevel_type_raw_source[] =
  "int8 slave_id\n"
  "int8 func_code\n"
  "int32 write_addr\n"
  "int32 read_addr\n"
  "int8 write_num\n"
  "int8 read_num\n"
  "int32[64] data\n"
  "";

static char msg_encoding[] = "msg";

// Define all individual source functions

const rosidl_runtime_c__type_description__TypeSource *
om_msgs__msg__Query__get_individual_type_description_source(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static const rosidl_runtime_c__type_description__TypeSource source = {
    {om_msgs__msg__Query__TYPE_NAME, 17, 17},
    {msg_encoding, 3, 3},
    {toplevel_type_raw_source, 107, 107},
  };
  return &source;
}

const rosidl_runtime_c__type_description__TypeSource__Sequence *
om_msgs__msg__Query__get_type_description_sources(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static rosidl_runtime_c__type_description__TypeSource sources[1];
  static const rosidl_runtime_c__type_description__TypeSource__Sequence source_sequence = {sources, 1, 1};
  static bool constructed = false;
  if (!constructed) {
    sources[0] = *om_msgs__msg__Query__get_individual_type_description_source(NULL),
    constructed = true;
  }
  return &source_sequence;
}
