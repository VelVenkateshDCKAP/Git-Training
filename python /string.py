class String(str, Formatter):

    def __key__(self):
        return "String Methods"
    
    def truncate(self, count=0, reverse=True):
        if reverse:
            return self[:(len(self) - count)]
        else:
            return self[count:]

