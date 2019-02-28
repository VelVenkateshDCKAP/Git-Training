class MathsModifier(object):

    def __init__(self, *args, **kwargs):
        self.field_id = kwargs.get("field_id", None)
        self.data = kwargs.get("data", {})
        self.metadata = kwargs.get("metadata", {})
        self.meta_index = kwargs.get("meta_index", 0)
        self.field_index = kwargs.get("field_index", 0)
        self.value = kwargs.get("code_value", None)


    def add(self):
        """
        To add two numbers
        :return:
        """
        pass


    def subtract(self):
        """
        To subtract two numbers
        :return:
        """
        pass


    def multiply(self):
        """
        To multiply two numbers
        :return:
        """
        pass


    def divide(self):
        """
        To divide two numbers
        Eg:- a = 10
             b = 6
        :returns: 1.666
        """
        pass


    def floor_division(self):
        """
        To divide two numbers and returns the minimum
        rounded value
        Eg:- a = 10
             b = 6
        :returns: 1
        """
        pass


    def power(self):
        """
        To manipulate the power value

        eg:- a = 10
             b = 2
        :returns: a power b(10 power 2) = 10 * 10 = 100
        """
        pass


    def modulo(self):
        """
        TO return the remainder of the division
        operation
        Eg:- a = 10
             b = 6
        :return: a / b --> remainder = 4
        """
        pass