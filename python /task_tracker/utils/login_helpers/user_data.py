from flask import current_app
from werkzeug.local import LocalProxy


#Replicates the current user funtionality of login manager
#Loads the user using the session id.
#Sets the User Object or Anonymous object in the current user
from task_tracker.utils.login_helpers.login_utils import get_session_id
from task_tracker.utils.login_helpers.loginmanager import load_user

current_user = LocalProxy(lambda:load_user(get_session_id(current_app.role if 'role' in dir(current_app) else None)) )
