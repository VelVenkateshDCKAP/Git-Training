from flask import Blueprint, request

from task_tracker.forms.task_forms import TaskForm
from task_tracker.utils.login_helpers.decorators import login_required
from task_tracker.utils.response_utils import render_template
from task_tracker.utils.utils import save_task, send_task_email

task_app = Blueprint(__name__, __name__)

@task_app.route("/admin/add/task", methods=["GET", "POST"])
@login_required
def add_task():
    """
    Add Task
    :return:
    """
    form = TaskForm()
    if request.method == "POST":
        if form.validate_on_submit():
            form_data = request.form.to_dict()
            form_data["assignedTo"] = form.assignedTo.data
            save_task(form_data)

    return render_template("add_task.html", form=form)