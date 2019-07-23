import unittest

from pyfair.model.model_input import FairDataInput
from pyfair.utility.fair_exception import FairException


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
        """Ensure le_1_check works"""
        # Run items above one where they shouldn't and check for exception
        with self.assertRaises(FairException):
            self._input._check_le_1('Action', constant=5)
        with self.assertRaises(FairException):        
            self._input._check_le_1('Vulnerability', p=5)
        with self.assertRaises(FairException):        
            self._input._check_le_1('Control Strength', mean=5, stdev=2)
        with self.assertRaises(FairException):        
            self._input._check_le_1('Threat Capability', low=2, mode=5, high=10)

    def test_check_parameters(self):
        """Ensure missing keywords will throw an error or work normally"""
        # Constant
        self._input._check_parameters(self._input._gen_constant, constant=20)
        with self.assertRaises(FairException):
            self._input._check_parameters(self._input._gen_constant, p=4)
        # Betapert
        self._input._check_parameters(self._input._gen_pert, low=1, mode=4, high=10)
        with self.assertRaises(FairException):
            self._input._check_parameters(self._input._gen_pert, mode=4)
        # Check normal
        self._input._check_parameters(self._input._gen_normal, mean=4, stdev=2) 
        with self.assertRaises(FairException):
            self._input._check_parameters(self._input._gen_normal, mean=4, constant=3) 
        # Check bernoulli
        self._input._check_parameters(self._input._gen_bernoulli, p=.2) 
        with self.assertRaises(FairException):
            self._input._check_parameters(self._input._gen_bernoulli, mean=4) 

    def test_check_pert(self):
        """Ensure PERT checks are accuate"""
        pass
        #with self.assertRaises(FairException):
            #self._input._check_pert(low=-2, mode=

    def test_check_generation(self):
        pass
    
    def test_check_generation_multi(self):
        pass
    
    def test_gen_curve(self):
        pass


if __name__ == '__main__':
    unittest.main()
