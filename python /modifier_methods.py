

from modifier_main import get_module_name, get_klass, get_klass_name, get_method

available_modifiers = ["concat", "convertor", "decimalizer", "expression", "group", "truncate"]

params = {
    "str": {
        "upper": {},
        "partition": {
            "separation":{"required":True},
        },
        "startswith": {
            "prefix":{"required":True},
            "start":{"required":False, "default":None},
            "end":{"required":False, "default":None}
        },
        "lstrip": {
            "prefix":{"required":False, "default":" "}
        },
        "swapcase": {},
        "rjust": {
            "width":{"required":True},
            "fillchar":{"required":False, "default":" "}
        },
        "rpartition": {
            "separation":{"required":True}
        },
        "replace": {
            "old":{"required":True},
            "new":{"required":True},
            "count":{"required":False, "default":None}
        },
        "islower": {},
        "endswith": {
            "suffix":{"required":True},
            "start":{"required":None},
            "end":{"required":None}
        },
        "splitlines": {
            "keepends":{"required":False, "default":False}
        },
        "zfill": {
            "count":{"required":True}
        },
        "expandtabs": {
            "tabsize":{"required":False, "default":None}
        },
        "strip": {
            "chars":{"required":False, "default":None}
        },
        "isdigit": {},
        "ljust": {
            "width":{"required":True},
            "fillchar":{"required":False, "default":" "}
        },
        "capitalize": {},
        "find": {
            "char":{"required":True},
            "start":{"required":False, "default":None},
            "end":{"required":False, "default":None}
        },
        "count": {
            "char":{"required":True},
            "start":{"required":False, "default":None},
            "end":{"required":False, "default":None}
        },
        "index": {
            "char":{"required":True},
            "start":{"required":False, "default":None},
            "end":{"required":False, "default":None}
        },
        "lower": {},
        "isupper": {},
        "join": {
            "array_values":{"required":True}
        },
        "center": {
            "width":{"required":True},
            "fillchar":{"required":False, "default":0}
        },
        "isalnum": {},
        "title": {},
        "rindex": {
            "char":{"required":True},
            "start":{"required":False, "default":None},
            "end":{"required":False, "default":None}
        },
        "rsplit": {
            "char":{"required":True},
            "maxsplit":{"required":False, "default":None},
        },
        "format": {},
        "rfind": {
            "char":{"required":True},
            "start":{"required":False, "default":None},
            "end":{"required":False, "default":None}
        },
        "istitle": {},
        "decode": {},
        "isalpha": {},
        "split": {
            "char":{"required":True},
            "maxsplit":{"required":False, "default":None},
        },
        "rstrip": {
            "chars":{"required":False},
        },
        "encode": {},
        "isspace": {}
        },
    "int": {
        "bit_length": {},
        "conjugate": {}
        },
    "list": {
        "count": {},
        "index": {
            "index":{"required":True},
            "start":{"required":False, "default":None},
            "end":{"required":False, "default":None}
        },
        "pop": {
            "index":{"required":False, "default":0}
        },
        "reverse": {},
        "extend": {
            "array_value":{"required":True}
        },
        "insert": {
            "index":{"required":True},
            "element":{"required":True}
        },
        "append": {
            "element":{"required":True}
        },
        "remove": {
            "element":{"required":True}
        },
        "sort": {
            "compare":{"required":False, "default":None},
            "key":{"required":False, "default":None},
            "reverse":{"required":False, "default":False}
        }
    }
}

import inspect

class Methods(object):

    def __init__(self, *args, **kwargs):
        self.modifier_type = kwargs.get("modifier_type", "all")


    def load_modifiers(self):
        """
        To load the available modifier method based on the
        type of the modifier requested
        :return:
        """
        subclassess = inheritors(self.__class__)
        modifiers = {"built-in":self.get_builtin_methods(subclassess), "custom":self.get_custom_methods()}
        print(modifiers)

    def get_builtin_methods(self, subclassess):
        """
        To get the builtin modifiers
        :return:
        """
        builtin_methods = []

        for klass in subclassess:
            builtin_methods.append(retrieve_class_based_builtin_methods(klass))

        return builtin_methods

    def get_custom_methods(self):
        """
        TO retrieve the custom modifiers
        :return:
        """
        methods = {}
        for modifiers in available_modifiers:
            method = get_method(get_klass(get_module_name(modifiers), get_klass_name(modifiers)), modifiers)
            method_spec = inspect.getargspec(method)
            methods[modifiers] = {}
            methods[modifiers]["definition"] = str("Modifier Definition")
            methods[modifiers]["params"] = {}

            while 'self' in method_spec.args:
                method_spec.args.pop(method_spec.args.index("self"))

            if method_spec.defaults:
                args = list(reversed(method_spec.args))
                optional = []
                for index, defaults in enumerate(method_spec.defaults):
                    methods[modifiers]["params"][args[index]] = {"required":False, "default":defaults}
                    method_spec.args.pop(method_spec.args.index(args[index]))

                if method_spec.args:
                    for args in method_spec.args:
                        methods[modifiers]["params"][args] = {"required": True}

                if optional:
                    methods[modifiers]["params"]["optional"] = optional


            else:
                for args in method_spec.args:
                    methods[modifiers]["params"][args] = {"required":True}

        return methods


def retrieve_class_based_builtin_methods(klass):
    """
    To retrieve the built-in methods based on the provided
    class.
    :param klass: Name of the class
    :return:
    """
    klasses = list(set([klass] + list(klass.__bases__)))
    klasses.pop(klasses.index(Methods))
    methods = {}
    for aclass in klasses:
        methods[str(aclass.__name__)] = {}
        for methodname, methodobj in aclass.__dict__.iteritems():
            if callable(methodobj) and not str(methodname).startswith("__") and not str(methodname).startswith("_") and methodname in params[aclass.__name__]:
                methods[aclass.__name__][methodname] = {"definition":str("Modifier Definition"), "params":params[aclass.__name__][methodname]}
        else:
            if not methods[aclass.__name__]:
                del methods[aclass.__name__]

    return methods



def inheritors(klass):
    subclasses = set()
    work = [klass]
    while work:
        parent = work.pop()
        for child in parent.__subclasses__():
            if child not in subclasses:
                subclasses.add(child)
                work.append(child)
    return list(subclasses)

class String(str, Methods):

    pass

class Integer(int, Methods):

    pass

class List(list, Methods):

    pass

Methods().load_modifiers()




