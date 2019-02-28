from flask import Flask
from flask_redis import Redis

from flask_mail import Mail


app = Flask(__name__)
mail = Mail(app)

from task_tracker.utils.login_helpers.loginmanager import login_manager
from task_tracker.controllers.authentication import login_app
from task_tracker.controllers.dashboard import dashboard_app
from task_tracker.controllers.task import task_app




def create_app(object_name):
    # config
    app.config.from_object(object_name)

    # app.config.update(
    #     DEBUG=True,
    #     SECRET_KEY='secret_xxx'
    # )
    # Redis Configs
    redis_instance = Redis()
    app.register_blueprint(login_app)
    app.register_blueprint(dashboard_app)
    app.register_blueprint(task_app)
    redis_instance.init_app(app)
    login_manager.init_app(app)

    return app