#default packages imports
import time
from bson import ObjectId

#flask/Framework imports
from flask import Response, redirect, abort, request, session, Blueprint

#local file imports
from task_tracker.mongo.collections import users
from task_tracker.utils.login_helpers.decorators import login_required, not_logged_in
from task_tracker.utils.login_helpers.login_configs import redis, admin_role, user_role
from task_tracker.utils.login_helpers.login_utils import verify_login, set_redis_session, expire_redis_session, \
    login_user
from task_tracker.utils.login_helpers.loginmanager import login_manager

login_app = Blueprint(__name__, __name__)



@login_app.route('/user')
@login_required
def home():
    """
    User Page
    :return:
    """
    return Response("Hello User!!")


@login_app.route('/admin')
@login_required
def admin():
    """
    Admin Page
    :return:
    """
    return Response("Hello Admin!!")


@login_app.route("/user/login", methods=["GET", "POST"])
@not_logged_in
def user_login():
    """
    To login the user
    :return:
    """
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = users.find_one({"email": username})
        is_verified, message = verify_login(user, password)
        if is_verified:
            login_user(user, admin=False)
            set_redis_session(user["role"])
            login_manager.error = False
            return redirect('/user/dashboard')
        else:
            return abort(Response(message))
    else:
        return Response('''
        <form action="" method="post">
            <p><input type=text name=username>
            <p><input type=password name=password>
            <p><input type=submit value=Login>
        </form>
        ''')


@login_app.route("/admin/login", methods=["GET", "POST"])
@not_logged_in
def admin_login():
    """
    To login the admin
    :return:
    """
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = users.find_one({"username": username})
        is_verified, message = verify_login(user, password, True)
        if is_verified:
            login_user(user, admin=True)
            set_redis_session(user["role"])
            login_manager.error = False
            return redirect('/admin/dashboard')
        else:
            return abort(Response(message))
    else:
        return Response('''
        <form action="" method="post">
            <p><input type=text name=username>
            <p><input type=password name=password>
            <p><input type=submit value=Login>
        </form>
        ''')



@login_app.route("/flush")
def flush_redis():
    redis.flushdb()
    session.clear()
    print redis
    return Response('<p>Flushed redis</p>')


@login_app.route("/timeout")
def timeout():
    redis.set("expiry", "test", ex=10)
    time.sleep(5)
    redis.pexpire("expiry", 10)
    redis.ttl("expiry")
    return Response('<p>Checked Time</p>')


@login_app.route("/admin/logout")
@login_required
def admin_logout():
    """
    To logout the admin
    :return:
    """
    session["loggedin"] = False
    expire_redis_session(admin_role)
    return redirect('/admin/login')


@login_app.route("/user/logout")
@login_required
def user_logout():
    """
    To logout the user
    :return:
    """
    session["loggedin"] = False
    expire_redis_session(user_role)
    return redirect('/user/login')


# handle login failed
@login_app.errorhandler(401)
def page_not_found(message):
    return Response('<p>{0}</p>'.format(message))









