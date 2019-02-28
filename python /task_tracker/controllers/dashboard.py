import datetime
from flask import Blueprint, Response, session, request, flash, redirect

from task_tracker.forms.task_forms import RegistrationForm, ConfirmUserForm
from task_tracker.mongo.collections import users
from task_tracker.utils.login_helpers.decorators import login_required, not_logged_in
from task_tracker.utils.login_helpers.login_utils import set_redis_session, generate_hash, login_user
from task_tracker.utils.response_utils import render_template
from task_tracker.utils.utils import is_user_exists, add_new_user, confirm_token
from task_tracker import login_manager

dashboard_app = Blueprint(__name__, __name__)

@dashboard_app.route("/user/dashboard")
@login_required
def user_dashboard():
    """
    Display Dahsboard of the user
    :return:
    """
    return Response('<p>User area {0}</p>'.format(session.get("email")))


@dashboard_app.route("/admin/dashboard")
@login_required
def admin_dashboard():
    """
    Display dashboard of the admin
    :return:
    """
    return render_template("sadashboard.html")


@dashboard_app.route("/admin/add/user", methods=["GET", "POST"])
@login_required
def add_user():
    """
    Display dashboard of the admin
    :return:
    """
    form = RegistrationForm()
    if request.method == "POST":
        if form.validate_on_submit():
            form_data = request.form.to_dict()
            if not is_user_exists(form_data):
                add_new_user(form_data)
                return render_template("confirmation.html", form=form)
            return render_template("add_user.html", errors="User Exists", form=form)
        return render_template("add_user.html", form=form)
    return render_template("add_user.html", form=form)


@dashboard_app.route("/admin/delete/user", methods=["GET", "POST"])
@login_required
def delete_user():
    """
    Display dashboard of the admin
    :return:
    """
    return render_template("sadashboard.html")


@dashboard_app.route('/confirm_email/<token>', methods=['GET', 'POST'])
@not_logged_in
def confirm_email(token):
    form = ConfirmUserForm()
    email = ''

    try:
        email = confirm_token(token)
    except:
        flash('The confirmation link is invalid or has expired.', 'danger')
        return redirect('/')

    if not email:
        flash('The confirmation link is invalid or has expired.', 'danger')
        return redirect('/')

    user = users.find_one({'email': email})
    if user['is_active']:
        flash('Account already confirmed. Please login.', 'success')
        return redirect('/login')

    if request.method == "POST":
        if form.validate_on_submit():
            users.update({'email': email}, {'$set': {
                'is_active': True,
                'confirmed_on': datetime.datetime.utcnow(),
                'password': generate_hash(request.values.get('password'))
            }})

            flash('You account has been successfully created. Thanks!', 'success')
            login_user(user, admin=False)
            set_redis_session(user["role"], force=True)
            login_manager.error = False
            return redirect('/user/dashboard')
            # login_user(User(email, user['first_name'] + ' ' + user['last_name']), admin=False)
        else:
            flash('Please fix the errors and proceed.', 'danger')

    return render_template('create_password.html', form=form)