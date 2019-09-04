import tempfile
import unittest

from pyfair.utility.database import FairDatabase


class TestFairViolinPlot(unittest.TestCase):

    def setUp(self):
        self._tf = tempfile.NamedTemporaryFile()
        self._db = FairDatabase(self._tf)

    def tearDown(self):
        self._tf.close()
        self._tf = None
        self._db = None

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