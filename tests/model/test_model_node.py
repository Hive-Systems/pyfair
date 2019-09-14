import unittest

from pyfair.model.model_tree import FairDependencyNode


class TestFairDependencyTree(unittest.TestCase):

    _node = None

    def setUp(self):
        self._node = FairDependencyNode(name='test_node')
    
    def tearDown(self):
        self._node = None

    def test_creation(self):
        """Run first. Test creation (done by setUp)"""
        # If you manage to f*** up something here, you deserve it.
        pass
        

    def test_add_child(self):
        """Ensure addition of child nodes is done correctly."""
        child_node = FairDependencyNode(name='child')
        self._node.add_child(child_node)
        # Ensure added node is attached to parent.
        self.assertEqual(len(self._node.children), 1)
        # Ensure added item is child
        self.assertTrue(self._node.children[0] is child_node)
        # Ensure child has a parent, and that parent is self._node
        self.assertTrue(child_node.parent is self._node)

    
    def test_add_parent(self):
        """Test addition of parent."""
        parent_node = FairDependencyNode(name='parent')
        self._node.add_parent(parent_node)
        # Ensure added node is attached to child as 'parent' attribute
        self.assertTrue(self._node.parent)


if __name__ == '__main__':
    unittest.main()
