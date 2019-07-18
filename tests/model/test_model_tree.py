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
        # Now mimic calculation and assert that calculated but not ready for calculation
        tree.update_status('Risk', 'Calculated')
        self.assertFalse(tree.ready_for_calculation())
        self.assertTrue(tree.calculation_completed())   

    def test_propogation(self):
        pass
    
    def test_statuses(self):
        pass


if __name__ == '__main__':
    unittest.main()