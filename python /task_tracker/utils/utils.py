import datetime, math,re, pymongo

from flask import url_for
from flask_mail import Message
from itsdangerous import URLSafeTimedSerializer


from task_tracker.mongo.collections import users, search_fields
from task_tracker.mongo.models.task import Tasks
from task_tracker.mongo.models.users import Users
from task_tracker import app, mail
from task_tracker.utils.constants import filter_prefix
from task_tracker.utils.db_utils import save_to_db
from task_tracker.utils.login_helpers.login_configs import user_role
from task_tracker.utils.response_utils import render_template


def is_user_exists(form_data):
    """
    To check whether the user exists
    :param form_data:
    :type dict

    :return:
    """
    user_data = users.find_one({"email":form_data.get("email", None)})
    return True if user_data else False


def add_new_user(form_data):
    """
    To add new user into database
    :param form_data:
    :type dict

    :return:
    """

    data = {"role":user_role, "is_active":False, "course":form_data["course"].lower(), "taskId":[]}
    save_to_db(model=Users, data=form_data, additional_data=data)
    send_confirmation_mail(form_data['email'])


def save_task(form_data):
    """
    To save the task into the database
    :param form_data: Task Data
    :return:
    """
    data = {"isDeleted":False, "completedBy":[], "submittedBy":[], "answers":[]}
    task_obj = save_to_db(model=Tasks, data=form_data, additional_data=data)
    update_user(task_obj)


def update_user(task_obj):
    """
    To update the user collection with task id
    :param task_obj:
    :return:
    """
    if task_obj.assignedTo:
        user_data = list(users.find(generate_filters('email', ','.join(task_obj.assignedTo))))
        for user in user_data:
            user["taskId"].append(task_obj._id)
            save_to_db(model=Users, data=user)
        send_task_email(task_obj)



def send_confirmation_mail(email):
    token = generate_confirmation_token(email)
    confirm_url = url_for('task_tracker.controllers.dashboard.confirm_email', token=token, _external=True)
    html = render_template('email_confirmation.html', confirm_url=confirm_url)
    subject = "Please confirm your email address with Task Tracker"
    send_email([email], subject, html)

def send_task_email(task_obj):
    title = task_obj.task_name
    due = task_obj.due_date
    input = task_obj.input
    output = task_obj.output
    description = task_obj.problem_statement
    hints = task_obj.hints
    html = render_template('task_email.html', task_title=title, input=input, output=output, hints=hints, due_by=due,
                           description=description)
    subject = "Todays({0}) Task".format(datetime.datetime.now().date())
    send_email(task_obj.assignedTo, subject, html)



def generate_confirmation_token(email):
    serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
    return serializer.dumps(email, salt=app.config['SECURITY_PASSWORD_SALT'])


def send_email(to, subject, template):
    msg = Message(
        subject,
        recipients=to,
        html=template,
        sender=app.config['MAIL_USERNAME']
    )
    mail.send(msg)


def confirm_token(token, expiration=3600):
    serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
    try:
        email = serializer.loads(
            token,
            salt=app.config['SECURITY_PASSWORD_SALT'],
            max_age=expiration
        )
    except:
        return False
    return email


def get_query_filters(request):
    """
    To create filters using the query params
    requested
    :param request:
    :return:
    """
    filters = {}
    for key, value in request.args.iteritems():
        if key.startswith(filter_prefix):
            generate_filters(key[len(filter_prefix)::], value, filters)

    if not filters["$and"]:
        del filters["$and"]

    return filters

def generate_filters(key, value, filters={}):
    """
    To generate
    :param key: filter key
    :param value: filter values
    :param filters: default filters
    :return:
    """
    if ',' in value:
        filters = {"$and":[]}
        values = value.split(',')
        filters["$and"].append({"$or": [{key: check_and_convert_to_bool(str(val))
        if isinstance(val, unicode) else check_and_convert_to_bool(val)} for val in values]})
    else:
        filters[key] = check_and_convert_to_bool(str(value)) if isinstance(value, unicode) \
            else check_and_convert_to_bool(value)

    return filters

def get_field_filters(request):
    """
    To create field filter query using the
    query params
    :param request:
    :return:
    """
    fields_query = {}
    field = request.args.get('fields', '')
    if field:
        fields = field.split(',')
        for key in fields:
            fields_query[key] = 1

    return fields_query if fields_query else None


def get_sort_query(request):
    """
    To sort the data in the requested order
    :param request:
    :return:
    """

    return [(request.args.get('sort_key', '_id'), safely_cast_to_int(request.args.get('sort_order', '1'), force=True))]


def get_limit(request):
    """
    To return the limit value to restrict the
    number of documents to be retrieved from DB
    :param request:
    :return:
    """
    return safely_cast_to_int(request.args.get("limit",10), force=True, zero=True)


def get_page(request):
    """
    To get the requested page number from
    the request
    :param request:
    :return:
    """
    return safely_cast_to_int(request.args.get("page", 1), force=True, zero=False)


def check_and_convert_to_bool(value):
    """
    To check and convert the value into boolean object
    :param value:
    :return:
    """
    value = safely_cast_to_int(value)
    if isinstance(value, str):
        lower_value = value.lower()
        bool_value = True if lower_value == "true" else (False if lower_value == "false" else value)
        return bool_value


def get_search_query(request, model):
    """
    To generate search query using query
    params

    if exact search is requested, then the indexing is
    performed and then the full text search will be
    executed

    if not exact search, regex search will be implemented
    on the search fields declared for the models
    :param request:
    :return:
    """

    model.drop_indexes()
    search_query = {"$or":[]}
    query = str(request.args.get("search",''))
    exact = check_and_convert_to_bool(request.args.get("exact","false"))
    if query:
        fields = search_fields.get(str(model.name), [])
        if exact:
            set_index(model, fields)
            search_query = {"$text":{"$search":query}}
            return search_query

        search_text = re.compile('.*{0}.*'.format(query))
        search_query["$or"] = [ {field:search_text} for field in fields ]
        return search_query

    return None


def set_index(model, fields):
    """
    To retrieve the search fields on a
    particular collection and create index on the
    retrieved field if index does not exists
    :param model:
    :return:
    """
    model.create_index([(key, pymongo.TEXT) for key in fields], name=str(model.name))


def safely_cast_to_int(value, force=False, zero=False):
    """
    To convert the value into int
    :param value:
    :return:
    """
    try:
        return int(value)
    except ValueError as exc:
        print exc
        zero_or_one = 0 if zero else 1
        return zero_or_one if force else value


def get_skip(request):
    """
    To calculate the skip count for aiding
    to retrive the requested page data
    :param request:
    :return:
    """
    page = get_page(request)
    limit = get_limit(request)
    if page > 1:
        return ((page - 1) * limit)
    return 0


def is_int(value, key="value"):
    """
    To validate whether the value is integer
    :param value: integer value
    :type int

    :param key: Content to be showed in error message
    :type str
    :return:
    """
    if not isinstance(value, int):
        raise ValueError("{0} must be an integer".format(key))


class Pagination(object):
    """
    Class to create pagination
    """
    def __init__(self, *args, **kwargs):
        self.query_obj = kwargs.get("model", None)
        self.limit = kwargs.get("limit", 10)
        self.page = kwargs.get("page",1)
        self.validate()
        self.page_data = {}
        self.is_paginated = False


    def validate(self):
        """
        To validate the query
        :return:
        """
        is_int(self.limit, "limit")
        is_int(self.page, "page")


    def paginate_data(self):
        """
        To generate page data
        :return:
        """
        self.total_obj = self.query_obj.count()
        self.page_data = self.getAvailablePages(self.page, self.total_obj, self.limit)
        self.is_paginated = True
        return self

    def getAvailablePages(self, page, total, limit, variation=2):
        """
        To calculate the pages count, next page and previous page
        :param page: Request Page number
        :type int

        :param total: Total pages
        :type int

        :param limit: data per page
        :type int
        :return:
        """

        pager = {'pages': [], 'prev': 0, 'next': 0}

        total_pages = math.ceil(total / float(limit))
        start, end = 1, total_pages

        max_page = variation * 2 + 1

        if total_pages > max_page:
            if page - variation > 0:
                start = page - variation

            if 0 < page + variation < total_pages:
                end = page + variation

            if end < max_page <= total_pages:
                end = max_page

            if total_pages - variation < page and total_pages >= max_page:
                start = total_pages - (variation * 2)

        pager['pages'] = [x for x in range(int(start), int(end + 1))]

        if page != 1:
            pager['prev'] = page - 1
        if page != total_pages:
            pager['next'] = page + 1

        pager['total'] = total_pages

        return pager


    @property
    def data(self):
        """
        property method to retrieve the query obj
        :return:
        """
        return self.query_obj


    @property
    def pages(self):
        """
        property method to retrieve the page information

        :raises: NotImplementedError if this method in accessed before calling self.paginate_data() method
        :return:
        """
        if self.is_paginated:
            return self.paginate_data().page_data
        raise NotImplementedError("You can access 'Pagination().pages' only after calling Pagination().paginate_data()")




