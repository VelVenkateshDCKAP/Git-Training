import pickle

from flask.signals import Namespace

from task_tracker.mongo.models.users import Users
from task_tracker.mongo.user import User
from task_tracker.utils.login_helpers.anonymous import AnonymousUserMixin
from task_tracker.utils.login_helpers.login_configs import LOGIN_MESSAGE, redis

_signals = Namespace()

#: Sent when a user is logged in. In addition to the app (which is the
#: sender), it is passed `user`, which is the user being logged in.
user_logged_in = _signals.signal('logged-in')

#: Sent when a user is logged out. In addition to the app (which is the
#: sender), it is passed `user`, which is the user being logged out.
user_logged_out = _signals.signal('logged-out')


class CustomLoginManager(object):

    """
    Class which replicates the functionalities of
    flask login Login Manager class
    """
    def __init__(self, app=None, add_context_processor=False):
        #: A class or factory function that produces an anonymous user, which
        #: is used when no one is logged in.
        self.anonymous_user = AnonymousUserMixin

        #: The name of the view to redirect to when the user needs to log in.
        #: (This can be an absolute URL as well, if your authentication
        #: machinery is external to your application.)
        self.login_view = None

        #: Names of views to redirect to when the user needs to log in,
        #: per blueprint. If the key value is set to None the value of
        #: :attr:`login_view` will be used instead.
        self.blueprint_login_views = {}

        #: The message to flash when a user is redirected to the login page.
        self.login_message = LOGIN_MESSAGE

        #: The name of the view to redirect to when the user needs to
        #: reauthenticate.
        self.refresh_view = None


        #: The mode to use session protection in. This can be either
        #: ``'basic'`` (the default) or ``'strong'``, or ``None`` to disable
        #: it.
        self.session_protection = 'basic'

        #: If present, used to translate flash messages ``self.login_message``
        #: and ``self.needs_refresh_message``
        self.localize_callback = None

        self.user_callback = None

        self.unauthorized_callback = None

        self.needs_refresh_callback = None

        self.header_callback = None

        self.request_callback = None

        if app is not None:
            self.init_app(app, add_context_processor)

    def init_app(self, app, add_context_processor=False):
        '''
        Configures an application. This registers an `after_request` call, and
        attaches this `LoginManager` to it as `app.login_manager`.

        :param app: The :class:`flask.Flask` object to configure.
        :type app: :class:`flask.Flask`
        :param add_context_processor: Whether to add a context processor to
            the app that adds a `current_user` variable to the template.
            Defaults to ``True``.
        :type add_context_processor: bool
        '''
        app.login_manager = self

        self._login_disabled = app.config.get('LOGIN_DISABLED', False)

        if add_context_processor:
            app.context_processor(load_user())

login_manager = CustomLoginManager()



def load_user(session_id=None):
    """
    Loads the user from redis cache using
    the session id

    :param session_id:
    :type str

    :returns: User Object if session id is found in redis cache
    :returns: Anonymous User object, if it fails to fetch the session data
    """
    redis_data = redis.get(session_id) if session_id else None
    if not redis_data:
        return AnonymousUserMixin()
    user_data = pickle.loads(redis_data)
    user = Users({'email':user_data["email"]})
    role = False
    try:
        user.load()
        if '_id' in user:
            if 'role' in user and user['role'] == "admin":
                role = True
            return User(user.email, user.fullname, role)
    except Exception as e:
        print e

    return AnonymousUserMixin()

