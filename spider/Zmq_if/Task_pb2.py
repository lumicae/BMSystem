# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: Task.proto

import sys
_b=sys.version_info[0]<3 and (lambda x:x) or (lambda x:x.encode('latin1'))
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
from google.protobuf import descriptor_pb2
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor.FileDescriptor(
  name='Task.proto',
  package='zmq_if',
  syntax='proto2',
  serialized_pb=_b('\n\nTask.proto\x12\x06zmq_if\"X\n\x04Task\x12\x0c\n\x04hash\x18\x01 \x02(\t\x12\x10\n\x08rel_path\x18\x02 \x02(\t\x12\x17\n\x0ftask_descriptor\x18\x03 \x02(\x0c\x12\x17\n\x0ftarget_addition\x18\x04 \x02(\x0c')
)
_sym_db.RegisterFileDescriptor(DESCRIPTOR)




_TASK = _descriptor.Descriptor(
  name='Task',
  full_name='zmq_if.Task',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='hash', full_name='zmq_if.Task.hash', index=0,
      number=1, type=9, cpp_type=9, label=2,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='rel_path', full_name='zmq_if.Task.rel_path', index=1,
      number=2, type=9, cpp_type=9, label=2,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='task_descriptor', full_name='zmq_if.Task.task_descriptor', index=2,
      number=3, type=12, cpp_type=9, label=2,
      has_default_value=False, default_value=_b(""),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='target_addition', full_name='zmq_if.Task.target_addition', index=3,
      number=4, type=12, cpp_type=9, label=2,
      has_default_value=False, default_value=_b(""),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  syntax='proto2',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=22,
  serialized_end=110,
)

DESCRIPTOR.message_types_by_name['Task'] = _TASK

Task = _reflection.GeneratedProtocolMessageType('Task', (_message.Message,), dict(
  DESCRIPTOR = _TASK,
  __module__ = 'Task_pb2'
  # @@protoc_insertion_point(class_scope:zmq_if.Task)
  ))
_sym_db.RegisterMessage(Task)


# @@protoc_insertion_point(module_scope)
