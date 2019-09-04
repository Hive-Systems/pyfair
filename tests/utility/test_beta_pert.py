import unittest

import numpy as np

from pyfair.utility.beta_pert import FairBetaPert
from pyfair.utility.fair_exception import FairException


class TestFairViolinPlot(unittest.TestCase):

    _CORRECT_MEAN = 23.848266752716704

    def setUp(self):
        np.random.seed(42)

    def test_beta_pert(self):
        """Test BetaPert generation"""
        # Test correct usage
        fbp = FairBetaPert(
            low=5,
            mode=20,
            high=50,
            gamma=2
        )
        variates = fbp.random_variates(1_000)
        mean = variates.mean()
        self.assertEquals(mean, self._CORRECT_MEAN)
        # Test incorrect usage
        self.assertRaises(
            FairException,
            FairBetaPert,
            low=5,
            mode=5,
            high=5
        )


if __name__ == '__main__':
    unittest.main()
