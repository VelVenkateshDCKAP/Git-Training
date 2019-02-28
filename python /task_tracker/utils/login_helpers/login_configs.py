

#External packages import
import redis as base_redis

redis = base_redis.StrictRedis(host = 'localhost')


#Constants
user_role = 'user'
admin_role = 'admin'
admin_session = "_1"
user_session = "_0"
expires_in = 3000 #seconds
admin_path = "admin"
admin_path_list = ["/{0}".format(admin_path), admin_path, "{0}/".format(admin_path), "/{0}/".format(admin_path)]
admin_dashboard = "/admin/dashboard"
user_dashboard = "/user/dashboard"
admin_login = "/admin/login"
user_login = "/user/login"
LOGIN_MESSAGE = "Please Login to access this page"
COOKIE_NAME = 'remember_token'
EXEMPT_METHODS = set(['OPTIONS'])
HASHING_UPDATE = False
DEFAULT_HASHING  = False






