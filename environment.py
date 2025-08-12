class Environment:
    def __init__(self, parent=None):
        self.store = {}
        self.parent = parent
    
    def get(self, name):
        if name in self.store:
            return self.store[name]
        elif self.parent:
            return self.parent.get(name)
        else:
            raise Exception(f"Undefined variable: {name}")
    
    def set(self, name, value):
        self.store[name] = value