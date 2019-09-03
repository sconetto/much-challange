import os
import random
from uuid import uuid4

from api1 import API1


class API2(API1):
    def create(self, data: dict):
        """Store one new object."""
        self._maybe_crash()
        new_obj = {**data, "id": uuid4()}
        self._storage[new_obj["id"]] = new_obj
        return new_obj

    @staticmethod
    def _maybe_crash():
        """Will this crash? No one knows. Very exciting."""
        if random.random() < 0.01:
            os._exit(0)
