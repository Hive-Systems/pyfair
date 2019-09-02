import unittest
import warnings

from pyfair.model.model import FairModel
from pyfair.model.meta_model import FairMetaModel
from pyfair.report.simple_report import FairSimpleReport


class TestFairSimpleReport(unittest.TestCase):

    def test_generate_image(self):
        """Check HTML content can be generated"""
        model_1 = FairModel(name='Model', n_simulations=10)
        model_1.input_data('Loss Event Frequency', mean=10, stdev=1)
        model_1.input_data('Loss Magnitude', low=0, mode=10, high=100)
        model_1.calculate_all()
        meta_model_1 = FairMetaModel(
            name='Meta', 
            models=[model_1, model_1]
        ).calculate_all()
        # Suppress warnings for number of figures generated
        with warnings.catch_warnings(record=False):
            warnings.simplefilter("ignore")
            fsr = FairSimpleReport([model_1, meta_model_1])
            _ = fsr._construct_output()
        # There are minor differences in data due to runtime data being
        # inlucded in the output. As of right now there's no easy way to
        # check this data to ensure content doesn't change from run-to-run.


if __name__ == '__main__':
    unittest.main()
