**Do as much as you can, it's not necessary to solve all the challenges. A well-documented, well-committed solution for the first challenge is better than an unreadable solution for all three.** *(Though it'd be interesting to see your solution for #3)*

All tasks build up on each other. **Commit** as often and add as much **documentation** as you think is reasonable. Create a new branch when you start a new task. (This folder should be a repository, else initialise one here.)

Contact us if you have any questions, or something seems wrong. Being able to communicate questions and do requirements engineering is an important skill.

Don't modify `apiX.py` files. You may add new files, just make sure it is clear which code relates to which challenge (or just use the `challengeX.py` files).

## 1. Product group tree

In this task we want to transfer a list of product groups (e.g. Vegetables, Beef, Oil) from an external database into our system. These product groups have a tree hierarchy, based on their `parent_id` and `children_ids`.

In `product_groups.json` we have a list of dicts of the following structure:

```python
{
    "id": int
    "name": str
    "parent_id": int
    "children_ids": List[int]
}
```

e.g.

```python
[{
    "id": 1,
    "name": "oil",
    "parent_id": None,
    "children_ids": [2,3]
},
{
    "id": 2,
    "name": "sunflower oil",
    "parent_id": 1,
    "children_ids": []
},
{
    "id": 3,
    "name": "olive oil",
    "parent_id": 1,
    "children_ids": [4]
},
{
    "id": 4,
    "name": "extra virgin olive oil",
    "parent_id":  3,
    "children_ids": []
}]
```

We have an api for inserting data, which sets the id when creating a new object:

```python
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
```

Read out `product_groups.json` and create all objects in the new API.  
They should have the following fields (no children_ids necessary):

```
{
    "id": str
    "name": str
    "parent_id": str
    "ancestors": List[str]
}
```

`ancestors` should be a list of all names of the ancestors of a product group.  
E.g. for *extra virgin olive oil* it would be `["oil", "olive oil"]`.

In the end, all created objects should have only new ids.

## 2. Random crashes
The API now randomly crashes your program.

```python
import os
import random
from uuid import uuid4

import API1

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
```

Modify your program to handle this.  
You should be able to restart it and continue where it left off. No objects should be created multiple times. You are allowed to store data in local files.

**Don't use threading magic to catch the os._exit(0). Let the program exit.**


## 3. Product group tree #2 - Bulk

The API now has a bulk create method.

```python
from uuid import uuid4
import API2

class API3(API2):
    def bulk_create(self, data: List[dict]):
        """Store multiple objects."""
        self._maybe_crash()
        new_objs = [{**obj, "id": uuid4()} for obj in data]
        self._storage.update({obj["id"]: obj for obj in data})
        return new_objs
```

Assume that one bulk request takes as much as 5 singular requests.  
Optimise for speed by using bulk requests.
