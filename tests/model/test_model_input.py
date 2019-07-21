import unittest

from pyfair.model.model_input import FairDataInput


class TestFairModelInput(unittest.TestCase):

    _input = None

    def setUp(self):
        self._input = FairDataInput()
    
    def tearDown(self):
        self._input = None

    def test_creation(self):
        """Test creation is proper"""
        # Check self._le_1_keywords are in parameter map
        for keyword in self._input._le_1_keywords:
            self.assertTrue(keyword in self._input._parameter_map)
        # Do the same for self._required_keywords
        for keyword_list in self._input._required_keywords.values():
            for keyword in keyword_list:
                self.assertTrue(keyword in self._input._parameter_map)

    def test_le_1_check(self):
        pass

    def test_check_parameters(self):
        pass

    def test_check_generation(self):
        pass
    
    def test_check_generation_multi(self):
        pass
    
    def test_gen_curve(self):
        pass


if __name__ == '__main__':
    unittest.main()
