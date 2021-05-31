import unittest

from pyfair.model.model_input import FairDataInput
from pyfair.utility.fair_exception import FairException


class TestFairModelInput(unittest.TestCase):

    _input = None
    _COUNT = 100
    _MULTI = {
            'Reputational': {
                'Secondary Loss Event Frequency': {'constant': 4000}, 
                'Secondary Loss Event Magnitude': {'low': 10, 'most_likely': 20, 'high': 100},
            },
            'Legal': {
                'Secondary Loss Event Frequency': {'constant': 2000}, 
                'Secondary Loss Event Magnitude': {'low': 10, 'most_likely': 20, 'high': 100},        
            }
    }

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
            self._input._check_le_1('Probability of Action', constant=5)
        with self.assertRaises(FairException):
            self._input._check_le_1('Vulnerability', constant=5)
        with self.assertRaises(FairException):
            self._input._check_le_1('Control Strength', mean=5, stdev=2)
        with self.assertRaises(FairException):
            self._input._check_le_1('Threat Capability', low=2, most_likely=5, high=10)

    def test_check_parameters(self):
        """Ensure missing keywords will throw an error or work normally"""
        # Constant
        self._input._check_parameters(self._input._gen_constant, constant=20)
        with self.assertRaises(FairException):
            self._input._check_parameters(self._input._gen_constant)
        # Betapert
        self._input._check_parameters(self._input._gen_pert, low=1, most_likely=4, high=10)
        with self.assertRaises(FairException):
            self._input._check_parameters(self._input._gen_pert, most_likely=4)
        # Check normal
        self._input._check_parameters(self._input._gen_normal, mean=4, stdev=2) 
        with self.assertRaises(FairException):
            self._input._check_parameters(self._input._gen_normal, mean=4, constant=3) 
        # Check that negative numbers raise error
        with self.assertRaises(FairException):
            self._input._check_parameters(self._input._gen_normal, mean=-1, stdev=2) 

    def test_check_pert(self):
        """Ensure PERT checks are accuate"""
        # Check low > most_likely
        with self.assertRaises(FairException):
            self._input._check_pert(low=5, most_likely=2, high=10)
        # Check most_likely > high
        with self.assertRaises(FairException):
            self._input._check_pert(low=5, most_likely=12, high=10)

    def test_check_generation(self):
        """Run generation tests"""
        # Run basic PERT
        result = self._input.generate('Loss Event Frequency', self._COUNT, low=0, most_likely=10, high=20)
        self.assertTrue(len(result) == self._COUNT)
        # Basic normal
        result = self._input.generate('Loss Event Frequency', self._COUNT, mean=20, stdev=5)
        self.assertTrue(len(result) == self._COUNT)
        # Basic bernoulli
        result = self._input.generate('Vulnerability', self._COUNT, mean=.5, stdev=.3)
        self.assertTrue(len(result) == self._COUNT)
        # Basic constant
        result = self._input.generate('Loss Event Frequency', self._COUNT, constant=50)
        self.assertAlmostEqual(result.mean(), 50)
        # Make sure items are clipped at 0 and 1 where approprriate
        result = self._input.generate('Probability of Action', self._COUNT, mean=.5, stdev=2)
        self.assertTrue(max(result) <= 1)
        self.assertTrue(min(result) >= 0)
    
    def test_check_generation_multi(self):
        """Multi was such a terrible idea"""
        self._input.generate_multi('multi_Secondary Loss', self._COUNT, self._MULTI)


if __name__ == '__main__':
    unittest.main()
