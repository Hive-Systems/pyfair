import hashlib
import unittest

from pyfair.model.model import FairModel
from pyfair.model.meta_model import FairMetaModel
from pyfair.report.simple_report import FairSimpleReport


class TestFairSimpleReport(unittest.TestCase):

    def test_generate_image(self):
        """Check HTML content is consistent with previously generateds"""
        model_1 = FairModel(name='Model', n_simulations=10)
        model_1.input_data('Loss Event Frequency', mean=10, stdev=1)
        model_1.input_data('Loss Magnitude', low=0, mode=10, high=100)
        meta_model_1 = FairMetaModel(
            name='Meta', 
            models=[model_1, model_1]
        )
        fsr = FairSimpleReport([model_1, meta_model_1])
        output = fsr._construct_output()
        hashed = hashlib.sha256(output.encode('utf8'))
        digest = hashed.hexdigest()
        raise Exception(digest)


if __name__ == '__main__':
    unittest.main()
