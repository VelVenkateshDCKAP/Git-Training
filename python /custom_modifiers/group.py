class GroupModifier(object):

    def __init__(self, *args, **kwargs):
        self.field_id = kwargs.get("field_id", None)
        self.data = kwargs.get("data", {})
        self.metadata = kwargs.get("metadata")
        self.processed_id = kwargs.get("processed_id", {})


    def group(self, process_id=[], raw_value=None):
        """
        Grouping will combine the outputs of all the
        grouped elements

        Eg:- Expression :  (firstName or lastName) and company
             Data       :   cloras    or app       and DCKAP
             results    :   clorasDCKAP

        """
        if process_id:
            joined_data = ""
            for id in process_id:
                joined_data += str(self.processed_id.get(id, ""))

            return joined_data