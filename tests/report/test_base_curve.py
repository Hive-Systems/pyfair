import unittest

from pyfair.model.meta_model import FairMetaModel
from pyfair.model.model import FairModel
from pyfair.report.base_curve import FairBaseCurve
from pyfair.utility.fair_exception import FairException


class TestFairBaseCurve(unittest.TestCase):


    def setUp(self):
        self._fbc = FairBaseCurve()

    def tearDown(self):
        self._fbc = None

    def test_good_inputs(self):
        """Test base_curve for good inputs"""
        model = FairModel('model')
        meta = FairMetaModel('meta', models=[model, model])
        good_list = [model, meta, model]
        for input_item in [model, meta, good_list]:
            self._fbc._input_check(input_item)

    def test_bad_inputs(self):
        """Test base_curve for bad inputs."""
        model = FairModel('model')
        bad_input_1 = []
        bad_input_2 = [model, 'a', 1]
        bad_input_3 = 'abc'
        bad_list = [bad_input_1, bad_input_2, bad_input_3]
        for input_item in bad_list:
            self.assertRaises(
                FairException, 
                self._fbc._input_check,
                input_item,
            )
 
if __name__ == '__main__':
    unittest.main()
