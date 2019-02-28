from functools import wraps
from flask import redirect, current_app, request, session
from flask_login import login_required

from login_utils import check_and_set_session, check_loggedin, get_path, get_role
from login_configs import admin_role, admin_dashboard, user_dashboard, EXEMPT_METHODS


def login_required(func):
    """
    To check whether the user has logged in and accessing
    the desired controller
    :param func:
    :type func

    :return:
    """
    @wraps(func)
    def decorated_view(*args, **kwargs):
        role = get_role(get_path(request.url))
        current_app.role = role
        check_and_set_session(role)
        print current_app.login_manager.error
        if request.method in EXEMPT_METHODS:
            return func(*args, **kwargs)
        elif current_app.login_manager._login_disabled:
            return func(*args, **kwargs)
        elif not session.get("loggedin", False) or current_app.login_manager.error:
            return redirect(current_app.login_manager.login_view)
        return func(*args, **kwargs)
    return decorated_view


def not_logged_in(func):
    """
    Decorator to check whether the admin is logged_in

    If the admin is logged_in, redirect the admin to dashboard
    :param func:
    :type func

    :return:
    """
    @wraps(func)
    def decorated_view(*args, **kwargs):
        role = get_role(get_path(request.url))
        current_app.role = role
        is_redirect = check_loggedin(role)
        if is_redirect:
            return redirect(admin_dashboard) if role == admin_role else redirect(user_dashboard)
        return func(*args, **kwargs)

    return decorated_view
