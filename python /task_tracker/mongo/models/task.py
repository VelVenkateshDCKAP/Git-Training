from task_tracker.mongo.collections import tasks
from task_tracker.mongo.models import BaseModel


class Tasks(BaseModel):
    collection = tasks

    def load(self):
        if self._id:
            coll = self.collection\
                    .find_one({"_id": self._id})
            if coll:
                self.update(coll)