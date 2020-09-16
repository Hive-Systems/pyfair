"""This module contains a tree class for model dependency tracking."""

from .model_node import FairDependencyNode


class FairDependencyTree(object):
    """A captive class tracking FAIR calculation dependencies.

    An instance of this class is created when a FairModel is instantiated.
    It is used to during the lifetime of the FairModel to track what data
    has been supplied to the model. Consequently it can be used to
    determine what further data is needed and what calculations can be
    performed.

    It is created from a group of nodes of type FairDependencyNode. When
    data is supplied, information is propogated down the tree and then
    up the tree when performing calculations. On its own, it is pretty
    dumb. The FairModel tells the tree what to do.

    Attributes
    ----------
    nodes : dict
        A dict with name string key and a FairDependencyNode value

    Notes
    -----
        http://pubs.opengroup.org/onlinepubs/9699919899/toc.pdf

    """
    def __init__(self):
        # Leaf nodes for reference
        self._leaf_nodes = []
        self._node_statuses = {}
        # Create and add nodes to tree
        self._root = FairDependencyNode('Risk')
        self._node_names = [
            'Risk', 
            'Loss Event Frequency', 
            'Threat Event Frequency', 
            'Vulnerability', 
            'Contact Frequency', 
            'Probability of Action', 
            'Threat Capability', 
            'Control Strength', 
            'Loss Magnitude', 
            'Primary Loss', 
            'Secondary Loss',
            'Secondary Loss Event Frequency', 
            'Secondary Loss Event Magnitude'
        ]
        # Initial tree setup
        self.nodes = {
            node_name: FairDependencyNode(node_name)
            for node_name
            in self._node_names
        }
        # Initial tree setup
        self._root = self.nodes['Risk']
        self._link_nodes()
        self._obtain_leaf_nodes(self._root)

    def ready_for_calculation(self):
        """Ensure there are no required items remaining

        Returns
        -------
        bool
            True if model is ready for calculation, otherwise False

        """
        # If there's required values return False
        if 'Required' in self._node_statuses.values():
            return False
        # Otherwise true
        else:
            return True

    def calculation_completed(self):
        """Determine whether the model has been completed

        Returns
        -------
        bool
            True if the calculation is complete, otherwise False

        """
        if self._root.status == 'Calculated':
            return True
        if self._root.status == 'Supplied':
            return True
        else:
            return False

    def update_status(self, node_name, new_status):
        """Notify node that data was provided

        This function notifies the node that the status has changed and
        then propogates data down the tree as necessary. For example, if
        data is supplied for a node, then all nodes underneath it are no
        longer required. The nodes are recursively updated to the bottom
        of the tree.

        In addition, information is also propgated up the tree. For
        example, if two nodes are calculabe (in other words, can be
        calculated), they can be calculated. In addition, if the
        calculation makes it possible for other nodes to be calculated,
        those will be calculated up the tree.

        Parameters
        ----------
        node_name : str
            The node in self.nodes that will be updated
        new_status : str
            The new status with which to update the node

        Example
        -------
        >>> # usually captive, but we're instantiating here
        >>> tree = FairDependencyTree()
        >>> # This will update nodes below (and above)
        >>> tree.update_status('Loss Event Frequency', 'Supplied')
        >>> tree.update_status('Loss Magnitude', 'Supplied')

        """
        # Get the target node
        node = self.nodes[node_name]
        # If data is supplied
        if new_status == 'Supplied':
            node.status = 'Supplied'
            # Let child nodes know they are no longer required
            for child_node in node.children:
                self._propogate_down(child_node)
            # Let parent nodes know they should check for their deps
            for node in self._leaf_nodes:
                self._propogate_up(node)
        # Calculated status requires no propogation
        if new_status == 'Calculated':
            node.status = 'Calculated'
        # Update node status dict
        self._obtain_status(self._root)

    def get_node_statuses(self):
        """Simple getter to obtain node statuses.

        Returns
        -------
        dict
            A dict with keys of node names and values of node statuses

        """
        return self._node_statuses

    def _link_nodes(self):
        """Links the nodes to allow tree traversing.

        At time of __init__() this method is run. It goes through each
        node in a predefined sequence and attaches child notes to the
        parent nodes.

        """
        # Node dict alias for brevity
        nodes = self.nodes
        # Add branches to root
        nodes['Risk'].add_child(nodes['Loss Event Frequency'])
        nodes['Risk'].add_child(nodes['Loss Magnitude'])
        # Loss Event Frequency Branch
        nodes['Loss Event Frequency'].add_child(nodes['Threat Event Frequency'])
        nodes['Loss Event Frequency'].add_child(nodes['Vulnerability'])
        # Threat Event Frequency Subbranch
        nodes['Threat Event Frequency'].add_child(nodes['Contact Frequency'])
        nodes['Threat Event Frequency'].add_child(nodes['Probability of Action'])
        # Vulnerability Subbranch
        nodes['Vulnerability'].add_child(nodes['Control Strength'])
        nodes['Vulnerability'].add_child(nodes['Threat Capability'])
        # Loss Magnitude Branch
        nodes['Loss Magnitude'].add_child(nodes['Primary Loss'])
        nodes['Loss Magnitude'].add_child(nodes['Secondary Loss'])
        # Secondary Loss Subbranch
        nodes['Secondary Loss'].add_child(nodes['Secondary Loss Event Frequency'])
        nodes['Secondary Loss'].add_child(nodes['Secondary Loss Event Magnitude'])

    def _obtain_status(self, node):
        """Traverse the tree and record the statuses

        This is a helper function to update the dict of statuses after
        changes are made via update_status.

        """
        self._node_statuses[node.name] = node.status
        for node in node.children:
            self._obtain_status(node)

    def _obtain_leaf_nodes(self, node):
        """Traverse the tree and record the leaf nodes. 

        Only run once, ideally. Leaf nodes are required when updating the
        tree from the bottom.

        """
        if len(node.children) == 0:
            self._leaf_nodes.append(node)
        for child_node in node.children:
            self._obtain_leaf_nodes(child_node)

    def _propogate_down(self, node):
        """Update child node status down from root to leaf nodes"""
        # Update node since children and subchildren no longer needed
        node.status = 'Not Required'
        # Recursively call for children
        for child_node in node.children:
            self._propogate_down(child_node)

    def _propogate_up(self, node):
        """Update parent node statuses up to root node.

        This is considerably more complicated than _propogate_down(). The
        reason for this is that for each node where the status is required,
        it is necessary to go to the parent nodes to see if that node can
        now be calculated. It then recursively calls the function on the
        parent node (until it reaches the root, which has no parent).

        """
        if node.parent:
            parent_node = node.parent
            # If it was Not Required, Supplied, or Calculated, it stays the same
            if parent_node.status in ['Not Required', 'Supplied', 'Calculated', 'Calculable']:
                pass
            # If it is Required, check to see if parent's child nodes now allow for calculation
            # I.E. if all are either 'Calculable', 'Calculated', or 'Supplied'
            elif parent_node.status == 'Required':
                # Get statuses
                statuses = [
                    child_node.status 
                    for child_node 
                    in parent_node.children
                ]
                # Get a bool for each of the statuses
                status_allows_for_calculation = [
                    status in ['Calculable', 'Calculated', 'Supplied']
                    for status
                    in statuses
                ]
                # If all statuses allow for calculation, change parent to "Calculable"
                if all(status_allows_for_calculation):
                    parent_node.status = 'Calculable'
            # Recursively call
            self._propogate_up(node.parent)
        # If no parent, do nothing.
        else:
            pass
