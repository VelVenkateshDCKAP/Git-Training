from flask_pymongo import MongoClient
from task_tracker.config import DevelopmentConfig as Config

client = MongoClient(Config.DB_HOST, Config.DB_PORT)
db = client[Config.DB_NAME]

users = db.users
tasks = db.tasks

search_fields = {
    str(users.name):["first_name", "last_name", "email", "course", "phone_number"]
}