from task_tracker.mongo.collections import users
from task_tracker.mongo.models import BaseModel


class Users(BaseModel):
    collection = users

    @property
    def fullname(self):
        return self.first_name + ' ' + self.last_name

    def load(self):
        if self.email:
            coll = self.collection\
                    .find_one({"email": self.email})
            if coll:
                self.update(coll)