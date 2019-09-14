"""Contains a node class for tracking calculation dependencies."""


class FairDependencyNode(object):
    """Represents the status of a given calculation for FairDependencyTree

    FairModel has a captive FairDependencyTree, and a FairDependencyTree
    is made of FairDependencyNodes. It is a simple structure that holds a
    status tag, and related nodes to allow for traversing the tree
    stucture.

    Parameters
    ----------
    name : str
        A human-readable designation for identification.


    Attributes
    ----------
    name : str
        A human-readable designation for identification.
    parent : pyfair.model.FairDependencyNode
        The single node immediately above the current node in the tree
        (default is None).
    children : list
        A list of the child nodes below the node in the tree (default
        is an empty list).
    status : {'Required', 'Not Required', 'Supplied', 'Calculable',
        'Calculated'}
        An identifier that gives the status of the node (default is
        'Required').

    """
    def __init__(self, name):
        self.name     = name
        self.parent   = None
        self.children = []
        # Statuses: Required, Not Required, Supplied, Calculable, Calculated
        self.status   = 'Required'

    def __repr__(self):
        return 'FairNode({}, Status={})'.format(self.name, self.status)

    def add_child(self, child):
        """Add a child to an individual node (orchestated by tree)

        Parameters
        ----------
        child : pyfair.model.FairDependencyNode
            A node to attach as a child

        """
        self.children.append(child)
        child.add_parent(self)
        return self

    def add_parent(self, parent):
        """Add a parent to an individual node (orchestated by tree)

        Parameters
        ----------
        parent : pyfair.model.FairDependencyNode
            A node to attach as a parent

        """
        self.parent = parent
        return self
