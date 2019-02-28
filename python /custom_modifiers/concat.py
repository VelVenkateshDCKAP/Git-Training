class ConcatModifier(object):

    def __init__(self, *args, **kwargs):
        self.field_id = kwargs.get("field_id", None)
        self.data = kwargs.get("data", {})
        self.metadata = kwargs.get("metadata")
        self.processed_id = kwargs.get("processed_id", {})
        self.meta_index = kwargs.get("meta_index", 0)
        self.field_index = kwargs.get("field_index", 0)


    def concat(self, process_id=[], raw_value=None):
        """
        Used to Concatenate two or more string and convert the string
        into a single string

        Eg:- str1 = "test"
             str2 = "try"
             returns "testtry"

        :returns: Concatenated String
        """
        if process_id:
            joined_data = ""
            for id in process_id:
                joined_data += str(self.processed_id.get(id, ""))

            return joined_data



