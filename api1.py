from uuid import uuid4


class API1:
    def __init__(self):
        self._storage = {}

    def get(self, obj_id: str):
        """Get an object."""
        return self._storage.get(obj_id)
    
    def create(self, data: dict):
        """Store one new object."""
        new_obj = {**data, "id": uuid4()}
        self._storage[new_obj["id"]] = new_obj
        return new_obj
