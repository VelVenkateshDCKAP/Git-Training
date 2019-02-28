class ExpressionModifier(object):

    def __init__(self, *args, **kwargs):
        self.field_id = kwargs.get("field_id", None)
        self.data = kwargs.get("data", {})
        self.metadata = kwargs.get("metadata")
        self.processed_id = kwargs.get("processed_id", {})

    def expression(self, logical, process_id=[], raw_value=None):
        """
        Based on the logical operations user requested the
        resulting data will be calculated

        Eg:- data:       firstName = "cloras", lastName="India"
             expression: and
             results:    clorasIndia

             data:       firstName = "cloras", lastName="India"
             expression: or
             results:    cloras


        """
        if process_id and logical == "or":
            for id in process_id:
                if self.processed_id.get(id, None):
                    return self.processed_id.get(id)

        elif process_id and logical == "and":
            joined_data = ""
            for id in process_id:
                joined_data += self.processed_id.get(id, "")

            return joined_data

