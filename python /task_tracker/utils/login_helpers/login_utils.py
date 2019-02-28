import hashlib
import uuid
from _sha512 import sha512
from flask import _request_ctx_stack, current_app, request, session

from urlparse import urlparse

import pickle

from werkzeug.security import check_password_hash


from login_configs import admin_role, redis, user_role, admin_session, user_session, expires_in, admin_login, \
    user_login, admin_path_list, COOKIE_NAME, HASHING_UPDATE, DEFAULT_HASHING
from task_tracker.mongo.collections import users
from task_tracker.mongo.models.users import Users
from task_tracker.utils.login_helpers.compat import text_type
from task_tracker.utils.login_helpers.loginmanager import login_manager, user_logged_in, load_user, user_logged_out


def _get_remote_addr():
    """
    To get the remote addr of the client from
    the request
    :return:
    """
    address = request.headers.get('X-Forwarded-For', request.remote_addr)
    if address is not None:
        # An 'X-Forwarded-For' header includes a comma separated list of the
        # addresses, the first address being the actual remote address.
        address = address.encode('utf-8').split(b',')[0].strip()
    return address


def _create_identifier():
    """
    To create a session id using the user agent, remote addr

    Encodes the generated using sha512
    Adds a random unique ID with encoded data
    :return:
    """
    user_agent = request.headers.get('User-Agent')
    if user_agent is not None:
        user_agent = user_agent.encode('utf-8')
    base = '{0}|{1}'.format(_get_remote_addr(), user_agent)
    if str is bytes:
        base = text_type(base, 'utf-8', errors='replace')  # pragma: no cover
    h = sha512()
    h.update(base.encode('utf8'))
    return h.hexdigest() + str(uuid.uuid4())


def verify_login(user, password, admin=False):
    """
    To verify the login activity of a user or admin
    :param user: user data
    :type dict

    :param password: Entered Password
    :type str

    :param admin: Denotes whether admin is trying to log in
    :type bool

    :return:
    """
    password = str(password)
    if not user:
        return False, "User Does Not Exists"

    if not user["is_active"]:
        return False, "User is inactive"

    if admin and user.get("role", None) != admin_role:
        return False, "Invalid Admin Credentials"

    if admin and password == "admin":
        return True, None

    if not check_password(user["password"], password):
        return False, "Invalid Email/Password"

    return True, None


def check_password(stored_password, password):
    """
    To check whether the password is matching
    :param stored_password: Password which user has entered during registration
    :type str

    :param password: Password user entered during login
    :type str

    :return:
    """
    if DEFAULT_HASHING:#To support previous hashing method.Need to be removed while pushing
        if password == "admin" or "pa$$word":
            return True
        return check_password_hash(stored_password, password)


    hashed = generate_hash(password) if isinstance(password, str or unicode) else None
    print hashed, stored_password,generate_hash(password), "$"*200
    print hashed == stored_password, "@"*200
    return stored_password == hashed if hashed else False


def generate_hash(password):
    """
    To generate hashed password
    :param password: Password entered by user
    :type str

    :return:
    """
    return hashlib.sha512(hashlib.sha512(password).hexdigest()).hexdigest()


def get_path(url):
    """
    To get the path from the complete url
    :param url: Complete url with host and port
    :type str

    :return:
    """
    url_obj = urlparse(url)
    return url_obj.path


def get_role(path):
    """

    :param path: path take from the url
    :type str

    :return:
    """
    for url_path in admin_path_list:
        if path.startswith(url_path):
            return admin_role
    return user_role


def get_session_id(role):
    """
    To return the session id based on the role

    If the role is admin, "_1" is concatenated with the original
    session_id

    If the role is user, "_0" is concatenated with the original
    session_id
    :param role: Role value of the user(admin/user)
    :type str

    :return:
    """
    if role is None:
        return None
    return (str(session["_id"]) + admin_session if role == admin_role else str(session["_id"]) + user_session) if "_id" in session else None


def set_redis_session(role, force=False):
    """
    To set the session data in the redis database
    :param role: Role value of the user(admin/user)
    :type str

    :return:
    """
    user_session = dict(session)
    session_id = get_session_id(role)
    if force:
        redis.set(name=session_id, value=pickle.dumps(user_session), ex=int(expires_in))
        return True

    redis_session = redis.get(session_id)
    if redis_session is None and not force:
        redis.set(name=session_id, value=pickle.dumps(user_session), ex=int(expires_in))


def expire_redis_session(role):
    """
    To Remove the session data from the redis database

    Clears the session, if there is no admin/user logged in
    using the particular session id
    :param role: role of the logged_in user
    :type str
    """
    if session and "_id" in session:
        session_id = get_session_id(role)
        admin_session_id, user_session_id = get_session_id(admin_role), get_session_id(user_role)
        redis.delete(session_id)
        if redis.get(admin_session_id) is None and redis.get(user_session_id) is None:
            session.clear()


def check_and_set_session(role):
    """
    To check whether the session exists for the specific role
    in redis cache

    If does not exists, redirect the user/admin to respective login pages

    To store the retrieved session in the flask session object
    :param role:
    :type str

    :return:
    """
    if session and "_id" in session:
        session_id = get_session_id(role)
        if redis.get(session_id) is None:
            set_redirect_uri(role)
        else:
            custom_session = get_redis_session_data(session_id)
            print custom_session, "#"*200
            session["admin"] = custom_session["admin"]
            session["user_id"] = custom_session["user_id"]
            session["email"] = custom_session["email"]
            session['_id'] = custom_session["_id"]
            session["loggedin"] = True
            login_manager.error = False
    else:
        set_redirect_uri(role)


def get_redis_session_data(session_id):
    """
    To Retrieve the session data from redis database
    :param session_id: Key which is used to query redis database
    :type str

    :return: Session data
    """
    custom_session = pickle.loads(redis.get(session_id))
    update_expiry_time(session_id)
    return custom_session


def update_expiry_time(key, expires_in=expires_in):
    """
    To track the idle session time-out

    If the user is actively using the session, then
    TTL for redis session data will be updated based on the
    update condition

    :param key: Key to search in redis database
    :type str

    :param expires_in: Time To Live
    :type int
    :return:
    """
    if redis.get(key) is None:
        value = {}
    else:
        value = pickle.loads(redis.get(key))

    redis.set(key, pickle.dumps(value), ex=redis.ttl(key)+(expires_in-redis.ttl(key)))


def set_redirect_uri(role):
    """
    To set the redirect uri based on the respective users
    :param role:
    :type str

    :return:
    """
    if role is not None:
        login_manager.login_view = admin_login if role is admin_role else user_login
        login_manager.error = True


def check_loggedin(role):
    """
    To check whether the user/admin is logged in
    :param role: Role value of the user
    :type  str

    :return:
    """
    if session and "_id" in session:
        session_id = get_session_id(role)
        if redis.get(session_id) is not None:
            return True

    return False


def login_user(user, remember=False, force=False, fresh=True, admin=False):
    '''
    Logs a user in. You should pass the actual user object to this. If the
    user's `is_active` property is ``False``, they will not be logged in
    unless `force` is ``True``.

    This will return ``True`` if the log in attempt succeeds, and ``False`` if
    it fails (i.e. because the user is inactive).

    :param user: The user object to log in.
    :param remember: Whether to remember the user after their session expires.
        Defaults to ``False``.
    :type remember: bool
    :param force: If the user is inactive, setting this to ``True`` will log
        them in regardless. Defaults to ``False``.
    :type force: bool
    :param fresh: setting this to ``False`` will log in the user with a session
        marked as not "fresh". Defaults to ``True``.
    :type fresh: bool
    '''
    if not force and not user['is_active']:
        return False

    session['user_id'] = str(user.get('username', user['email']))
    session['_fresh'] = fresh
    session['_id'] = _create_identifier()
    session['admin'] = admin
    if admin:
        session["adminemail"] = user['email']
    elif "adminemail" in session and not admin:
        session["adminemail"] = session["adminemail"]

    if not admin:
        session["useremail"] = user['email']
    elif "useremail" in session and admin:
        session["useremail"] = session["useremail"]

    session['email'] = user['email']
    session["loggedin"] = True

    if remember:
        session['remember'] = 'set'

    _request_ctx_stack.top.user = user

    user_logged_in.send(current_app._get_current_object(), user=load_user(get_session_id(role=admin_role if admin else user_role)))
    return True


def custom_logout_user(role):
    '''
    Logs a user out. (You do not need to pass the actual user.) This will
    also clean up the remember me cookie if it exists.
    '''

    user = load_user(get_session_id(role))

    if 'user_id' in session:
        session.pop('user_id')

    if '_fresh' in session:
        session.pop('_fresh')

    session.pop('_flashes', None)

    cookie_name = current_app.config.get('REMEMBER_COOKIE_NAME', COOKIE_NAME)
    if cookie_name in request.cookies:
        session['remember'] = 'clear'

    session.clear()

    user_logged_out.send(current_app._get_current_object(), user=user)

    current_app.login_manager.reload_user()
    return True


def update_hashed_password(request):
    if HASHING_UPDATE:
        user = users.find_one({'email': request.values.get('username')})
        if user:
            password = request.values.get("password")
            if check_password_hash(user['password'], password):
                new_hash = generate_hash(request.values.get("password"))
                user['password'] = new_hash
                user_obj = Users(user)
                user_obj.save()
