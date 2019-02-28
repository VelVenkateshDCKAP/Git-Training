import copy


class ConvertorModifier(object):

    def __init__(self, *args, **kwargs):
        self.field_id = kwargs.get("field_id", None)
        self.data = kwargs.get("data", {})
        self.metadata = kwargs.get("metadata")
        self.code_value = kwargs.get("code_value", None)
        self.meta_index = kwargs.get("meta_index", 0)
        # self.field_index = kwargs.get("field_index", 0)

    def convertor(self, current, new):
        """
        To Modify the data with a static raw data from the user input

        Eg:- Original data            {country:"India"}
             Requested Modification   {country:"IN"}

        :returns: Modified JSON data
        """
        parent = self.metadata[self.meta_index][self.field_id]['values']['parent']
        value = current if new is None else new
        if parent:
            self.update_dict(parent, self.data, value)
            return value

        else:
            self.data[self.metadata[self.meta_index][self.field_id]['values']['code']] = value
            return value


    def update_dict(self, parent, data, value):
        """
        To update the value in the data if the data
        is a nested dictionary
        :param parent: list of parents
        :param data: data dict in which value to be updated
        :param value: Value to be updated in data dict
        :return:
        """
        if parent:
            if isinstance(data[parent[0]], dict):
                self.update_dict(parent[1:], data[parent[0]], value)
        else:
            data[self.metadata[self.meta_index][self.field_id]['values']['code']] = value


