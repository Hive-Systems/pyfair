import unittest

import matplotlib

from pyfair.model.meta_model import FairMetaModel
from pyfair.model.model import FairModel
from pyfair.report.base_report import FairBaseReport
from pyfair.utility.fair_exception import FairException


class TestFairBaseReport(unittest.TestCase):

    _CALLER_SOURCE_DOCSTRING = "\"\"\"Script to create and run a test suite.\"\"\""
    _BASE64_BYTES = bytes([100, 100, 100, 100, 100])
    _BASE64_BYTES_TAG = '<img  src="data:image/png;base64, ZGRkZGQ=" alt=""/>'
    _BASE64_FIG_TAG_FIRST_50 = '<img  src="data:image/png;base64, iVBORw0KGgoAAAAN'

    def setUp(self):
        self._fbr = FairBaseReport()
        self._model_1 = FairModel('model1', n_simulations=5)
        self._model_1.input_data('Risk', mean=100, stdev=5)
        self._model_2 = FairModel('model2', n_simulations=5)
        self._model_2.input_data('Risk', mean=1000, stdev=50)
        self._metamodel = FairMetaModel(
            name='meta', 
            models=[self._model_1, self._model_2],
        )

    def tearDown(self):
        self._fbr = None
        self._model_1 = None
        self._model_2 = None
        self._metamodel = None

    def test_caller_source(self):
        """Test setting and getting of caller source"""
        cs = self._fbr._get_caller_source()
        cs_line_1 = cs.splitlines()[0]
        self.assertEquals(self._CALLER_SOURCE_DOCSTRING, cs_line_1)

    def test_input_check(self):
        """Test the validity of the input check"""
        # Create inputs
        bad_model = 'Not a model'
        model = FairModel(name='model')
        bad_meta = 0
        meta = FairMetaModel(name='metamodel', models=[model, model])
        model_list = [model, meta]
        bad_model_list_1 = []
        bad_model_list_2 = [model, bad_model]
        # Test good items
        for good_item in [model, meta, model_list]:
            self._fbr._input_check(good_item)
        # Test bad items
        for bad_item in [bad_model, bad_meta, bad_model_list_1, bad_model_list_2]: 
            self.assertRaises(
                FairException,
                self._fbr._input_check,
                bad_item
            )

    def test_base64ify(self):
        """Test base64ify"""
        tag = self._fbr.base64ify(self._BASE64_BYTES)
        self.assertEquals(tag, self._BASE64_BYTES_TAG)

    # DO NOT TEST to_html or _construct_output. Those are done by subclass.
 
    def test_fig_to_img_tag(self):
        """Convert fig to image tag"""
        fig = matplotlib.pyplot.figure()
        tag_first_50 = self._fbr._fig_to_img_tag(fig)[:50]
        self.assertEqual(tag_first_50, self._BASE64_FIG_TAG_FIRST_50)

    def test_get_tree(self):
        """Test tree creation creation"""
        self._fbr._get_tree(self._model_1)

    def test_get_distribution(self):
        """Test distribution creation"""
        self._fbr._get_distribution(self._model_1)
        self._fbr._get_distribution([self._model_1, self._model_2])

    def test_get_distribution_icon(self):
        """Test distribution icon creation"""
        self._fbr._get_distribution_icon(self._model_1, 'Risk')

    def test_get_exceedence_curves(self):
        """Test exceedence curve creation"""
        self._fbr._get_exceedence_curves(self._model_1)
        self._fbr._get_exceedence_curves([self._model_1, self._model_2])

    def test_get_violins(self):
        """Test violin creation"""
        self._fbr._get_violins(self._metamodel)

    def test_get_overview_table(self):
        """Test overvieww table"""
        self._fbr._get_overview_table({
            'name_1': self._model_1, 
            'name_2': self._model_2,
        })

    def test_get_model_parameter_table(self):
        """Get paramter table"""
        self._fbr._get_model_parameter_table(self._model_1)

    def test_get_metamodel_parameter_table(self):
        """Get metamodel paramter table"""
        self._fbr._get_metamodel_parameter_table(self._metamodel)


if __name__ == '__main__':
    unittest.main()
