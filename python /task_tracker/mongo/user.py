from task_tracker.mongo.collections import users


class User(object):

    def __init__(self, username, name, admin=False):
        self.name = name
        self.username = username
        self.admin = admin
        self.user = users.find_one({"email": username})
        self.id = self.user["_id"]

    @property
    def is_authenticated(self):
        return True

    @property
    def is_admin(self):
        return self.admin

    @property
    def is_active(self):
        return True

    @property
    def is_anonymous(self):
        return False

    @property
    def get_id(self):
        return self.username

    @staticmethod
    def validate_login(password_hash, password):
        from task_tracker.utils.login_helpers.login_utils import check_password
        return check_password(password_hash, password)