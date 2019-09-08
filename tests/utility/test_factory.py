import unittest

from pyfair.model.model import FairModel
from pyfair.utility.factory import FairModelFactory


class TestFairFactory(unittest.TestCase):

    _STATIC_ARGS = {'Loss Magnitude': {'constant': 5_000_000}}
    _VARIABLE_ARGS_1 = {'Loss Event Frequency': {'constant': 900}}
    _VARIABLE_ARGS_2 = {'Loss Event Frequency': {'constant': 100}}
    _VARIABLE_ARGS_3 = {'Loss Event Frequency': {'constant': 300}}
    _VARIABLE_ARGS_DICT = {
        'model_1': _VARIABLE_ARGS_1,
        'model_2': _VARIABLE_ARGS_2,
        'model_3': _VARIABLE_ARGS_3,
    }

    def setUp(self):
        self._fac = FairModelFactory(self._STATIC_ARGS)

    def tearDown(self):
        self._fac = None

    def test_gen_from_partial(self):
        """Test basic generation function via factory"""
        # Generate
        model = self._fac.generate_from_partial(
            'name',
            self._VARIABLE_ARGS_1
        )
        self.assertIsInstance(model, FairModel)
    
    def test_gen_from_partials(self):
        """Test generation of multiple items via factory"""
        # Generate
        models = self._fac.generate_from_partials(self._VARIABLE_ARGS_DICT)
        # Ensure proper number of argicles generated
        self.assertEquals(len(models), len(self._VARIABLE_ARGS_DICT))
        # Ensure they are all models
        for model in models:
            self.assertIsInstance(model, FairModel)



if __name__ == '__main__':
    unittest.main()