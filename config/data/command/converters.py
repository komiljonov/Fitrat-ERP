from django.urls import register_converter
from uuid import UUID


class StrOrUUIDConverter:
    regex = r"[0-9a-fA-F-]{36}|[\w-]+"  # Matches both UUID and normal strings

    def to_python(self, value):
        try:
            return UUID(value)  # Convert to UUID if possible
        except ValueError:
            return value  # Otherwise, keep it as a string

    def to_url(self, value):
        return str(value)


register_converter(StrOrUUIDConverter, "uid")
