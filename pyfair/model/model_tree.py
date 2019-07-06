'''This module contains two classes for model calculation dependency tracking.'''

from .model_node import FairDependencyNode


class FairDependencyTree(object):
    '''Represents status of a tree of calculations.
    
    See also:
        http://pubs.opengroup.org/onlinepubs/9699919899/toc.pdf
    
    '''
    
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
            'Contact', 
            'Action', 
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
        '''Ensure there are no required items remaining'''
        if 'Required' in self._node_statuses.values():
            return False
        else:
            return True
        
    def update_status(self, node_name, new_status):
        '''Notify node that data was provided'''
        node = self.nodes[node_name]
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
        return self._node_statuses

    def _link_nodes(self):
        # Node dict alias for brevity
        nodes = self.nodes
        # Add branches to root
        nodes['Risk'].add_child(nodes['Loss Event Frequency'])
        nodes['Risk'].add_child(nodes['Loss Magnitude'])
        # Loss Event Frequency Branch
        nodes['Loss Event Frequency'].add_child(nodes['Threat Event Frequency'])
        nodes['Loss Event Frequency'].add_child(nodes['Vulnerability'])
        # Threat Event Frequency Subbranch
        nodes['Threat Event Frequency'].add_child(nodes['Contact'])
        nodes['Threat Event Frequency'].add_child(nodes['Action'])
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
        '''Traverse the tree and record the statuses'''
        self._node_statuses[node.name] = node.status 
        for node in node.children:
            self._obtain_status(node)

    def _obtain_leaf_nodes(self, node):
        '''Traverse the tree and record the leaf nodes. Only run once, ideally.'''
        if len(node.children) == 0:
            self._leaf_nodes.append(node)
        for child_node in node.children:
            self._obtain_leaf_nodes(child_node)

    def _propogate_down(self, node):
        '''Update child node status down from root to leaf nodes'''
        # Update node since children and subchildren no longer needed
        node.status = 'Not Required'
        # Recursively call for children
        for child_node in node.children:
            self._propogate_down(child_node)
    
    def _propogate_up(self, node):
        '''Update parent node statuses up to root node'''
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
