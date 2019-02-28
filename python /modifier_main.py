import copy
import importlib


class Modifier(object):
    FIELD_TYPE_METHOD = "methods"
    FIELD_TYPE_CONVERTOR = "convertor"

    METADATA_LEVEL_FIELD = "field"
    METADATA_LEVEL_CROSS = "cross"
    METADATA_LEVEL_GROUP = "group"

    METHOD_TYPE_CUSTOM = "custom"
    METHOD_TYPE_BUILTIN = "built-in"

    def __init__(self, *args, **kwargs):
        self.modifiers = kwargs.pop("modifiers", None)
        self.data = kwargs.pop("data", None)
        self.metadata_level = ["group", "field", "cross"]
        self.fields_type = ["methods", "convertor"]
        self.errors = {}
        self.processed_id = {}
        self.set_fields_and_metadata()
        self.validate_modifiers()


    def set_fields_and_metadata(self):
        """
        To set the fields and meta data so that it can be accessed
        in handy throughout the class
        :return:
        """
        self.fields = self.modifiers.get("fields", {})
        self.metadata = self.modifiers.get("metadata", {})
        if not self.fields:
            self.errors['fields'] = "Fields Must not be empty"

        if not self.metadata:
            self.errors['metadata'] = "metadata should not be empty"


    def validate_modifiers(self):
        """
        TO validate the modifiers for the expected values in the
        JSON structure
        :return:
        """
        self.validate_metadata_type()
        self.validate_field_type()

        if self.errors:
            raise ValueError(self.errors)


    def validate_field_type(self):
        """
        To validate the type of the field in the
        JSON
        :return:
        """
        pass


    def validate_metadata_type(self):
        """
        To validate the type of the meta data provided
        by client side
        :return:
        """
        for index, data in enumerate(self.metadata):
            for key, value in data.iteritems():
                if self.metadata[index][key]["level"] not in self.metadata_level:
                    self.errors["metadata.%s.level" % key] = "Level should be any of %s" % self.metadata_level


    def get_modifier_data(self):
        """
        To get the modifier data
        :return:
        """
        for index, data in enumerate(self.metadata):
            for field_id, value in data.iteritems():
                self.meta_index = index
                self.apply_modifier(field_id, value["level"])

        return self.processed_id


    def apply_modifier(self, field_id, level):
        """
        To apply modifier on the particular field
        based on the modifier level
        :param field_id: ID of the field
        :param level: level of the modifier
        :return:
        """

        if level == self.METADATA_LEVEL_FIELD:
            self.process_field_level_modifiers(field_id)
        elif level ==  self.METADATA_LEVEL_CROSS:
            self.process_cross_level_modifiers(field_id)
        elif level == self.METADATA_LEVEL_GROUP:
            self.process_group_level_modifiers(field_id)


    def process_field_level_modifiers(self, field_id):
        """
        To process field level modifiers
        :param field_id:
        :return:
        """
        values = self.fields[field_id]["values"]
        if self.fields[field_id]["type"] == self.FIELD_TYPE_METHOD:
            for field_index, value in enumerate(values):
                self.process_method_modifiers(field_id, value, field_index)
        elif self.fields[field_id]["type"] == self.FIELD_TYPE_CONVERTOR:
            for field_index, value in enumerate(values):
                self.process_convertors(field_id, value, field_index)


    def process_cross_level_modifiers(self, field_id):
        """
        To process cross level modifiers
        :param field_id:
        :return:
        """
        values = self.fields[field_id]["values"]
        if self.fields[field_id]["type"] == self.FIELD_TYPE_METHOD:
            for field_index, value in enumerate(values):
                self.process_method_modifiers(field_id, value, field_index)


    def process_group_level_modifiers(self, field_id):
        """
        To process group level modifiers
        :param field_id:
        :return:
        """
        values = self.fields[field_id]["values"]
        if self.fields[field_id]["type"] == self.FIELD_TYPE_METHOD:
            for field_index, value in enumerate(values):
                self.process_method_modifiers(field_id, value, field_index)


    def process_method_modifiers(self, field_id, values, field_index):
        """
        *To process the method type modifiers
        *Stores the value in the processed_id
        *
        :param field_id:
        :return:
        """
        for modifier, value in values.iteritems():
            if value["type"] == self.METHOD_TYPE_CUSTOM:
                self.process_custom_methods(field_id, modifier, value, field_index)
            elif value["type"] == self.METHOD_TYPE_BUILTIN:
                self.process_builtin_methods(field_id, modifier, value, field_index)


    def process_convertors(self, field_id, values, field_index):
        """
        * TO Process the convertors and update the data
          based on the convertor values
        :param field_id:
        :return:
        """
        for convertor, params in values.iteritems():
            self.call_class_methods(get_module_name(convertor), convertor, convertor, field_id, field_index, params=params)


    def process_custom_methods(self, field_id, modifier, value, field_index):
        """
        Process the custom method modifiers
        :param field_id: Id of the fields on which modifier will be applied
        :param modifier: Modifier method name
        :param value: Instructions for executing the modifier method
        :return:
        """

        self.call_class_methods(get_module_name(modifier), modifier, modifier, field_id, field_index, params=value["params"])


    def process_builtin_methods(self, field_id, modifier, value, field_index):
        """
        Process the builtin methods based on the datatype
        of the input data
        :param field_id: Unique id of the field
        :param modifier: Name of the builtin method
        :param value: Execution instruction for builtin methods
        :return:
        """

        try:
            method = getattr(type(self.get_code_value_from_metadata(field_id)), modifier)
            self.processed_id[field_id] = method(self.get_code_value_from_metadata(field_id), *value["params"].values())
        except AttributeError as exc:
            print exc
            raise exc


    def call_class_methods(self, module, klass, method, field_id, field_index, params={}):
        """
        To call the methods in the imported class
        :param module: Module name from where klass should be imported
        :param klass: Name of the class
        :param method: Method Name
        :param params: Params for the method
        :param field_id: Id of the field in which modifier is being applied
        :return:
        """
        loaded_class = get_klass(module, get_klass_name(klass))
        if isinstance(params, dict):        #trigger()
            self.processed_id[field_id] = get_method(loaded_class, method)(
                loaded_class(field_id=field_id, metadata=self.metadata, data=self.data,
                             code_value=self.get_code_value_from_metadata(field_id),processed_id=self.processed_id,
                             field_index=field_index, meta_index=self.meta_index, modifier_obj=self),
                **params)


    def get_code_value_from_metadata(self, field_id):
        """
        To get the value of the code from the meta data
        :param field_id:
        :returns: Value of a field from data or from processed_id
        """

        if field_id in self.processed_id:
            return self.processed_id[field_id]

        else:
            for index, data in enumerate(self.metadata):
                if field_id in data:
                    if data[field_id]["level"] == self.METADATA_LEVEL_FIELD:
                        parent = self.metadata[index][field_id]['values']['parent']
                        if not parent:
                            return self.data[self.metadata[index][field_id]['values']['code']]

                        if parent:
                            source_data = copy.deepcopy(self.data)
                            for element in parent:
                                source_data = source_data.get(element)
                            return source_data[self.metadata[index][field_id]['values']['code']]



def get_method(klass, method):
    """
    To get the method of desired class
    :param klass:
    :param method:
    :return:
    """
    method = getattr(klass, method)
    return method

def get_module_name(modifier):
    """
    To build the module name based on the
    name of the modifier
    :param modifier:
    :return:
    """
    return "{0}.{1}".format("custom_modifiers",modifier)


def get_klass(module, klass):
    """
    TO load the class in the particular module
    :param module:
    :return:
    """
    imported_module = importlib.import_module(module, klass)
    klass = getattr(imported_module, klass)
    return klass


def get_klass_name(klass):
    """
    TO build the klass name based on the need
    of the modifier detection
    :param klass:
    :return:
    """
    try:
        return klass.capitalize()+"Modifier"
    except TypeError as exc:
        print exc
        return klass

if __name__ == "__main__":
    data = {
        "first_name":"ttcLoReSaa",
        "test":{"address":{"area":{"street":{"locality":{"country":"india"}}}}}
    }
    modifier_input = {
      "metadata": [
            {
              "1": {
                "level": "field",
                "values": {
                  "code": "first_name",
                  "parent": []
                }
              }
            },
            {
              "2": {
                "level": "field",
                "values": {
                  "code": "country",
                  "parent": ["test", "address", "area", "street", "locality"]
                }
              }
            },
            {
              "3": {
                "level": "cross",
                "values": {}
              }
            },
            {
              "4": {
                "level": "group",
                "values": 3
              }
            },
            {
              "5": {
                "level": "cross",
                "values": {}
              }
            }
      ],
      "fields": {
          "1": {
            "type": "methods",
            "values": [
                {
                  "truncate": {
                    "type": "custom",
                    "params": {
                      "count": 2,
                      "reverse": True
                    }
                  }
                },
                {
                  "replace": {
                    "type": "built-in",
                    "params": {
                      "find": "e",
                      "replace": "a"
                    }
                  }
                },
                {
                  "strip": {
                    "type": "built-in",
                    "params": {
                      "chars": "tt"
                    }
                  }
                },
                {
                  "capitalize":{
                     "type":"built-in",
                     "params":{}
                  }
                },
                {
                    "zfill": {
                        "type": "built-in",
                        "params": {
                            "count": 5
                        }
                    }
                },
                {
                    "isupper":{
                        "type":"built-in",
                        "params":{}
                    }
                }
            ]
          },
          "2": {
            "type": "convertor",
            "values": [
                {
                  "convertor": {
                    "current": "India",
                    "new": "IN"
                  }
                }
            ]
          },
          "3": {
            "type": "methods",
            "values": [
                {
                  "expression": {
                    "type": "custom",
                    "params": {
                      "process_id": [
                        "1",
                        "2"
                      ],
                      "raw_value": None,
                      "logical": "or"
                    }
                  }
                }
            ]
          },
          "4": {
            "type": "methods",
            "values": [
                {
                  "group": {
                    "params": {
                      "process_id": [
                        "1",
                        "2"
                      ],
                      "raw_value": None
                    },
                    "type": "custom"
                  }
                }
            ]
          },
          "5": {
            "type": "methods",
            "values": [
                {
                  "concat": {
                    "type": "custom",
                    "params": {
                      "process_id": [
                        "1",
                        "2"
                      ],
                      "raw_value": None
                    }
                  }
                }
            ]
          }
      }
    }

    import time
    start = time.time()
    modified_data = Modifier(data=data, modifiers=modifier_input).get_modifier_data()
    end = time.time()

    print "Execution Time:", end - start

    print modified_data
