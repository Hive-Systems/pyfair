class FairDependencyNode(object):
    '''Represents the status of a given calculation'''
    
    def __init__(self, name):
        self.name     = name
        self.parent   = None
        self.children = []
        # Statuses: Required, Not Required, Supplied, Calculable, Calculated
        self.status   = 'Required' 
        
    def __repr__(self):
        return 'FairNode({}, Status={})'.format(self.name, self.status)

    def add_child(self, child):
        self.children.append(child)
        child.add_parent(self)
        return self
    
    def add_parent(self, parent):
        self.parent = parent
        return self
