import unittest

from pyfair.model.model import FairModel
from pyfair.model.model import FairDependencyTree


class TestFairDependencyTree(unittest.TestCase):

    TOTAL_NODE_COUNT = 13
    LEAF_NODE_COUNT = 7

    def test_creation(self):
        """Check proper creation of tree."""
        tree = FairDependencyTree()
        self.assertEqual(len(tree.nodes), self.TOTAL_NODE_COUNT)
        self.assertEqual(len(tree._leaf_nodes), self.LEAF_NODE_COUNT)

    def test_inspections(self):
        """Check functions returning bools"""
        # Create tree ready for calculation
        tree = FairDependencyTree()
        tree.update_status('Loss Event Frequency', 'Supplied')
        tree.update_status('Loss Magnitude', 'Supplied')
        # Assert that it is ready for calculation but not complete
        self.assertTrue(tree.ready_for_calculation())
        self.assertFalse(tree.calculation_completed())
        # Now mimic calculation and assert complete
        tree.update_status('Risk', 'Calculated')
        self.assertTrue(tree.calculation_completed())   

    def test_downward_propogation(self):
        """Ensure propogation up and down the tree works"""
        tree = FairDependencyTree()
        # The supply two nodes
        tree.update_status('Loss Event Frequency', 'Supplied')
        tree.update_status('Loss Magnitude', 'Supplied')
        # Each of those nodes should now equal supplied
        statuses = tree.get_node_statuses()
        for node in [
            'Loss Event Frequency',
            'Loss Magnitude'
        ]:
            self.assertEqual(statuses[node], 'Supplied')
        # And inferior nodes should be 'Not Required'
        for node in [
            'Threat Event Frequency',
            'Vulnerability',
            'Contact',
            'Action',
            'Threat Capability',
            'Control Strength',
            'Primary Loss',
            'Secondary Loss',
            'Secondary Loss Event Frequency',
            'Secondary Loss Event Magnitude',
        ]:
            self.assertEqual(statuses[node], 'Not Required')

    def test_upward_propagation(self):
        """Ensure upward calculation propogation works"""
        tree = FairDependencyTree()
        # The supply three nodes
        tree.update_status('Loss Event Frequency', 'Supplied')
        tree.update_status('Primary Loss', 'Supplied')
        tree.update_status('Secondary Loss', 'Supplied')
        # Get statuses and check appropriate fields are calculable
        statuses = tree.get_node_statuses()
        for node in [
            'Risk', 
            'Loss Magnitude'
        ]:
            self.assertEqual(statuses[node], 'Calculable')
        # Now mark a node as calculated
        tree.update_status('Loss Magnitude', 'Calculated')
        statuses = tree.get_node_statuses()
        self.assertEqual(statuses['Loss Magnitude'], 'Calculated')


if __name__ == '__main__':
    unittest.main()
