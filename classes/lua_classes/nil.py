class NilClass:
    def __init__(self):
        pass

    def __str__(self):
        return "nil"
    
    def __repr__(self):
        return str(self)
    
    def __eq__(self, value):
        if isinstance(value , NilClass) : return True
        else : return False

NilClass.__name__ = "nil"
nil = NilClass()
