import httplib

from flask import jsonify
from flask.globals import _app_ctx_stack
from flask.templating import _render
from .login_helpers.user_data import current_user


def render_template(template_name_or_list, **context):
    """Renders a template from the template folder with the given
    context.

    :param template_name_or_list: the name of the template to be
                                  rendered, or an iterable with template names
                                  the first one existing will be rendered
    :param context: the variables that should be available in the
                    context of the template.
    """
    ctx = _app_ctx_stack.top
    context["current_user"] = current_user
    ctx.app.update_template_context(context)
    return _render(ctx.app.jinja_env.get_or_select_template(template_name_or_list),
                   context, ctx.app)



def get_response(**kwargs):
    response = {}
    response['data'] = kwargs.get("data", [])
    response['status'] = kwargs.get("status", httplib.OK)
    response["message"] = kwargs.get("message", "Success")

    if "error" in kwargs:
        response["error"] = kwargs.get("error")

    if "pages" in kwargs:
        pages = kwargs.get("pages", {'total': 1, 'prev': 0, 'pages': [1], 'next': 0})
        response['total'] = pages.get('total',1)
        response['prev'] = pages.get('prev', 0)
        response['pages'] = pages.get('pages', [1])
        response['next'] = pages.get('next', 0)

    return jsonify(response)



