import unittest

from pyfair.model.model import FairModel
from pyfair.model.meta_model import FairMetaModel
from pyfair.report.distribution import FairDistributionCurve


class TestFairBaseReport(unittest.TestCase):

    def setUp(self):
        self._model_1 = FairModel('model1', n_simulations=5)
        self._model_1.input_data('Loss Event Frequency', mean=100, stdev=5)
        self._model_1.input_data('Loss Magnitude', mean=1000, stdev=50)
        self._model_1.calculate_all()
        # Node model or iterable test will be done prior to instantiation
        self._fdc1 = FairDistributionCurve(self._model_1)
        self._fdc2 = FairDistributionCurve([
            self._model_1, 
            self._model_1
        ])

    def tearDown(self):
        self._fbr = None
        self._model_1 = None
        self._model_2 = None
        self._fdc1 = None
        self._fdc2 = None

    def test_generate_icon(self):
        "Test distribution icon generation"""
        for fdc in [self._fdc1, self._fdc2]:
            fdc.generate_icon('model1', 'Loss Event Frequency')
            self.assertRaises(
                KeyError,
                fdc.generate_icon,
                'model5',  
                'Vulnerability'
            )

    def test_generate_image(self):   
        """Test main distribution image generation"""     
        for fdc in [self._fdc1, self._fdc2]:
            fdc.generate_image()


if __name__ == '__main__':
    unittest.main()
