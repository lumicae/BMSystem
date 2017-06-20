import uuid

node = uuid.getnode()
mac  = uuid.UUID(int = node).hex[-12:]
print mac