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
  package='ZmqUtil',
  syntax='proto3',
  serialized_pb=_b('\n\nTask.proto\x12\x07ZmqUtil\"\x1a\n\x04Task\x12\x12\n\ndescriptor\x18\x01 \x01(\x0c\x62\x06proto3')
)
_sym_db.RegisterFileDescriptor(DESCRIPTOR)




_TASK = _descriptor.Descriptor(
  name='Task',
  full_name='ZmqUtil.Task',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='descriptor', full_name='ZmqUtil.Task.descriptor', index=0,
      number=1, type=12, cpp_type=9, label=1,
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
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=23,
  serialized_end=49,
)

DESCRIPTOR.message_types_by_name['Task'] = _TASK

Task = _reflection.GeneratedProtocolMessageType('Task', (_message.Message,), dict(
  DESCRIPTOR = _TASK,
  __module__ = 'Task_pb2'
  # @@protoc_insertion_point(class_scope:ZmqUtil.Task)
  ))
_sym_db.RegisterMessage(Task)


# @@protoc_insertion_point(module_scope)
