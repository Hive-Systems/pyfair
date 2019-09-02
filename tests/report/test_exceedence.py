import unittest

import numpy as np
import pandas as pd

from pyfair.model.model import FairModel
from pyfair.report.exceedence import FairExceedenceCurves


class TestFairExceedenceCurves(unittest.TestCase):

    _RISK = pd.Series([10_000, 20_000, 30_000])
    _SPACE = pd.Series(np.linspace(0, 30_000, 100))
    _MEAN_QUANTILE = 34
    _MEAN_PERCENT = 66

    def setUp(self):
        self._model_1 = FairModel('model1', n_simulations=5)
        self._model_1.input_data('Loss Event Frequency', mean=100, stdev=5)
        self._model_1.input_data('Loss Magnitude', mean=1000, stdev=50)
        self._model_1.calculate_all()
        # Node model or iterable test will be done prior to instantiation
        self._fec_1 = FairExceedenceCurves(self._model_1)
        self._fec_2 = FairExceedenceCurves([
            self._model_1, 
            self._model_1
        ])

    def tearDown(self):
        self._model_1 = None
        self._fec_1 = None
        self._fec_2 = None

    def test_generate_image(self):
        """Ensure generate_image() output"""
        for fec in [self._fec_1, self._fec_2]:
            fec.generate_image()

    def test_prob_data(self):
        """Test quantile generation"""
        quantiles, space = self._fec_1._get_prob_data(
            self._SPACE,
            self._RISK
        )
        self.assertAlmostEquals(self._MEAN_QUANTILE, quantiles.mean())

    def test_loss_data(self):
        """Test loss percentage gneration data"""
        space, percent = self._fec_1._get_loss_data(
            self._SPACE,
            self._RISK,
        )
        self.assertAlmostEquals(self._MEAN_PERCENT, percent.mean())


if __name__ == '__main__':
    unittest.main()
