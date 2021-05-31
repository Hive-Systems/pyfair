import unittest

from pyfair.model.model import FairModel
from pyfair.model.meta_model import FairMetaModel
from pyfair.report.jupyter import FairJupyterShim
from pyfair.utility.fair_exception import FairException


class TestFairJupyterShim(unittest.TestCase):

    def setUp(self):
        self._model_1 = FairModel('model_1', n_simulations=5)
        self._model_1.input_data('Loss Event Frequency', mean=100, stdev=5)
        self._model_1.input_data('Loss Magnitude', mean=1000, stdev=50)
        self._model_1.calculate_all()
        self._model_2 = FairModel('model_2', n_simulations=5)
        self._model_2.input_data('Loss Event Frequency', mean=10, stdev=5)
        self._model_2.input_data('Loss Magnitude', mean=100, stdev=50)
        self._model_2.calculate_all()
        self._metamodel_1 = FairMetaModel('metamodel_1', [self._model_1, self._model_2])
        self._metamodel_1.calculate_all()

    def tearDown(self):
        self._model_1 = None
        self._model_2 = None
        self._metamodel_1 = None

    def test_bad_inputs_creation(self):
        """Test whether bad inputs throw an error"""
        with self.assertRaises(FairException):
            inputs = [
                self._model_1,
                'ERROR'
            ]
            shim = FairJupyterShim(inputs, currency_prefix='€')

    def test_good_tree(self):
        """Test a tree with models"""
        inputs = [
            self._model_1,
            self._model_2,
        ]
        shim = FairJupyterShim(inputs, currency_prefix='€')
        output = shim.get_trees()

    def test_bad_tree(self):
        """Test tree with metamodel"""
        inputs = [
            self._metamodel_1,
            self._model_2,
        ]
        with self.assertRaises(FairException):
            shim = FairJupyterShim(inputs, currency_prefix='€')
            output = shim.get_trees()
    
    def test_get_distributions(self):
        """Test the distribution generation"""
        inputs = [
            self._metamodel_1,
            self._model_2,
        ]
        with self.assertRaises(FairException):
            shim = FairJupyterShim(inputs, currency_prefix='€')
            output = shim.get_distributions()
        self.assertTrue('combined' in output.keys())

    def test_exceedence_curves(self):
        """Test the exceedence curves"""
        inputs = [
            self._metamodel_1,
            self._model_2,
        ]
        with self.assertRaises(FairException):
            shim = FairJupyterShim(inputs, currency_prefix='€')
            output = shim.get_exceedence_curves()
        self.assertTrue('combined' in output.keys())

    def test_good_violin(self):
        """Test valid violin plot"""
        inputs = [
            self._metamodel_1,
        ]
        shim = FairJupyterShim(inputs, currency_prefix='€')
        output = shim.get_violins()

    def test_bad_violin(self):
        """Test invalid violin plot"""
        inputs = [
            self._model_2,
        ]
        with self.assertRaises(FairException):
            shim = FairJupyterShim(inputs, currency_prefix='€')
            output = shim.get_violins()


if __name__ == '__main__':
    unittest.main()
