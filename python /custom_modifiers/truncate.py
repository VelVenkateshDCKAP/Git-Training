class TruncateModifier(object):

    def __init__(self, *args, **kwargs):
        self.field_id = kwargs.get("field_id", None)
        self.data = kwargs.get("data", {})
        self.metadata = kwargs.get("metadata", {})
        self.meta_index = kwargs.get("meta_index", 0)
        self.field_index = kwargs.get("field_index", 0)
        self.value = kwargs.get("code_value", None)


    def __key__(self):
        return "String Methods"


    def truncate(self, count=0, reverse=True):
        """
        Removes the specific number of characters in the prefix
        or suffix of a string based on the params provided

        By default, removes character from the right of the string
        :param count: Defines the number of characters to be removed
        :param reverse: Set to True by default which means characters will be striped from right

        Eg:- Input:- string = "test"
                     count  = 2
                     results = "te"
        """
        if reverse:
            return self.value[:(len(self.value) - count)]
        else:
            return self.value[count:]


