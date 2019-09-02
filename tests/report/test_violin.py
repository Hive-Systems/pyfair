import unittest
import warnings

from pyfair.model.model import FairModel
from pyfair.model.meta_model import FairMetaModel
from pyfair.report.violin import FairViolinPlot


class TestFairViolinPlot(unittest.TestCase):

    def test_tree_graph_creation(self):
        """Test violin plot creation"""
        # There is little to test here other than simple creation
        # Whether it comes out OK or not ... ¯\_(ツ)_/¯
        model = FairModel(name='Test')
        model.input_data('Loss Magnitude', mean=50, stdev=5)
        model.input_data('Loss Event Frequency', low=10, mode=20, high=30)
        metamodel = FairMetaModel(name='Test Meta', models=[model, model])
        with warnings.catch_warnings(record=False):
            warnings.simplefilter("ignore")
            fvp = FairViolinPlot(metamodel)
            _, _ = fvp.generate_image() 


if __name__ == '__main__':
    unittest.main()
