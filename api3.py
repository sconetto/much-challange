from typing import List
from uuid import uuid4

from api2 import API2


class API3(API2):
    def bulk_create(self, data: List[dict]):
        """Store multiple objects."""
        self._maybe_crash()
        new_objs = [{**obj, "id": uuid4()} for obj in data]
        self._storage.update({obj["id"]: obj for obj in data})
        return new_objs
