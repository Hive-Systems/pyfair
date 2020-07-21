import unittest
import warnings

from pyfair.model.model import FairModel
from pyfair.report.tree_graph import FairTreeGraph


class TestFairTreeGraph(unittest.TestCase):

    # Test only dollars ... this is the defualt
    _DOLLAR_FORMAT_STRING = '${0:,.0f}'
    _FLOAT_FORMAT_STRING  = '{0:.2f}'
    _FORMAT_STRINGS = {
        'Risk'                           : _DOLLAR_FORMAT_STRING,
        'Loss Event Frequency'           : _FLOAT_FORMAT_STRING,
        'Threat Event Frequency'         : _FLOAT_FORMAT_STRING,
        'Vulnerability'                  : _FLOAT_FORMAT_STRING,         
        'Contact'                        : _FLOAT_FORMAT_STRING,
        'Action'                         : _FLOAT_FORMAT_STRING,
        'Threat Capability'              : _FLOAT_FORMAT_STRING,
        'Control Strength'               : _FLOAT_FORMAT_STRING,
        'Loss Magnitude'                 : _DOLLAR_FORMAT_STRING,
        'Primary Loss'                   : _DOLLAR_FORMAT_STRING,
        'Secondary Loss'                 : _DOLLAR_FORMAT_STRING,
        'Secondary Loss Event Frequency' : _DOLLAR_FORMAT_STRING,
        'Secondary Loss Magnitude'       : _DOLLAR_FORMAT_STRING,
    }

    def test_tree_graph_creation(self):
        """Test tree greaph creation"""
        # There is little to test here other than simple creation
        # Whether it comes out OK or not ... ¯\_(ツ)_/¯
        model = FairModel(name='Test')
        model.input_data('Loss Magnitude', mean=50, stdev=5)
        model.input_data('Loss Event Frequency', low=10, most_likely=20, high=30)
        model.calculate_all()
        with warnings.catch_warnings(record=False):
            warnings.simplefilter("ignore")
            ftg = FairTreeGraph(model, self._FORMAT_STRINGS)
            _, _ = ftg.generate_image()


if __name__ == '__main__':
    unittest.main()
