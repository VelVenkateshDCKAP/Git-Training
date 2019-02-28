

class BaseSerializer(object):

    def __init__(self, *args, **kwargs):
        self.initial_data = kwargs.get("data", None)
        self.data = kwargs.get("data", None)
        self.remove_fields = kwargs.get("remove_fields")
        self.selection_fields = kwargs.get("selection_fields")
        self.multiple = kwargs.get("multiple", False)
        self.format_data()
        self.validate()
        if self.remove_fields or self.selection_fields:
            self.pop_fields()


    def format_data(self):
        # object_id_to_string(self.data)
        pass

    def validate(self):
        """
        To validate the incoming data
        :return:
        """
        if self.remove_fields and self.selection_fields:
            raise ValueError("Cannot set both selection fields and Remove fields")

        if self.multiple and not isinstance(self.data, list):
            raise TypeError("If multiple is True, then data must be a list object")

        self.multiple = True if isinstance(self.data, list) else False
        self.remove = True if self.remove_fields else False

    def pop_fields(self):
        """
        To remove the fields from the data based on the selection field
        or remove fields
        :return:
        """
        fields = self.remove_fields if self.remove else self.selection_fields
        if not self.multiple:
            self.process_fields_removal(self.data, fields)
        else:
            for values in self.data:
                self.process_fields_removal(values, fields)


    def process_fields_removal(self, source_dict, fields):
        """
        Process the removal of fields from the data dict
        :param source_dict: Dict data values
        :param fields: Fields to be removed
        :return:
        """
        keys = source_dict.keys()
        for key in keys:
            if self.remove:
                if key in fields:
                    source_dict.pop(key, None)
            else:
                if key not in fields:
                    source_dict.pop(key, None)

    @property
    def get_data(self):
        """
        property method to get the removed data
        :return:
        """
        return self.data


class UserSerializer(BaseSerializer):


    pass

