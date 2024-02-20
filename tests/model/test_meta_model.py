import json
import unittest

import pandas as pd

from pyfair.model.meta_model import FairMetaModel
from pyfair.model.model import FairModel
from pyfair.utility.fair_exception import FairException


class TestFairMetaModel(unittest.TestCase):
    _RISK_TABLE_COLUMN_COUNT = 2
    _N_SAMPLES = 100
    _MODEL_JSON = '{     "Loss Event Frequency": {         "low": 20,         "mode": 100,         "high": 900     },     "Loss Magnitude": {         "low": 3000000,         "mode": 3500000,         "high": 5000000     },     "name": "Regular Model 1",     "n_simulations": 10000,     "random_seed": 42,     "model_uuid": "b6c6c968-a03c-11e9-a5db-f26e0bbd6dbc",     "type": "FairModel",     "creation_date": "2019-07-06 17:23:43.647370" }'
    _META_MODEL_JSON = '{     "Regular Model 1": {         "Loss Event Frequency": {             "low": 20,             "mode": 100,             "high": 900,             "gamma":4         },         "Loss Magnitude": {             "low": 3000000,             "mode": 3500000,             "high": 5000000,             "gamma":4         },         "name": "Regular Model 1",         "n_simulations": 10000,         "random_seed": 42,         "model_uuid": "b6c6c968-a03c-11e9-a5db-f26e0bbd6dbc",         "type": "FairModel",         "creation_date": "2019-07-06 17:23:43.647370"     },     "Regular Model 2": {         "Loss Event Frequency": {             "mean": 0.3,             "stdev": 0.1         },         "Loss Magnitude": {             "low": 2000000000,             "mode": 3000000000,             "high": 5000000000,            "gamma":4         },         "name": "Regular Model 2",         "n_simulations": 10000,         "random_seed": 42,         "model_uuid": "b6ca98a4-a03c-11e9-8ce0-f26e0bbd6dbc",         "type": "FairModel",         "creation_date": "2019-07-06 17:23:43.672336"     },     "name": "My Meta Model!",     "model_uuid": "b6cce298-a03c-11e9-b79f-f26e0bbd6dbc",     "creation_date": "2019-07-06 17:23:43.687336",     "type": "FairMetaModel" }'

    def setUp(self):
        # Static method instantiation
        self._meta = FairMetaModel.read_json(self._META_MODEL_JSON)

    def tearDown(self):
        self._meta = None

    def test_creation(self):
        """Test basic instantiation"""
        # Ensure existence of appropriate attributes
        self.assertTrue(self._meta._model_uuid)
        self.assertTrue(self._meta._creation_date)
        # Check that the table is of proper-ish
        self.assertEqual(
            len(self._meta._risk_table.columns), self._RISK_TABLE_COLUMN_COUNT
        )
        # Test regular instantiation
        m1 = FairModel.read_json(self._MODEL_JSON)
        m2 = FairModel.read_json(self._MODEL_JSON)
        self._meta = FairMetaModel("New Model", [m1, m2])
        # Throw garbage in metamodel
        self.assertRaises(
            FairException, FairMetaModel, "Garnage Name", ["Garbage Input"]
        )

    def test_read_json(self):
        """setUp covers most, so just test Model JSON fails"""
        # Ensure metamodel fails
        self.assertRaises(
            FairException, FairMetaModel.read_json, self._MODEL_JSON
        )

    def test_inspection(self):
        """Check the inspection methods"""
        # Check inspection methods
        self._meta.get_name()
        self._meta.get_uuid()
        # Check dataframe
        self.assertIsInstance(self._meta.export_results(), pd.DataFrame)
        # Check Params
        self.assertIsInstance(self._meta.export_params(), dict)

    def test_calculation(self):
        """Run a calulate all."""
        # Test regular instantiation
        m1 = FairModel.read_json(self._MODEL_JSON)
        m2 = FairModel.read_json(self._MODEL_JSON)
        self._meta = FairMetaModel("New Model", [m1, m2])
        # Test before
        self.assertFalse(self._meta.calculation_completed())
        # Calculate
        self._meta.calculate_all()
        # Test after
        self.assertTrue(self._meta.calculation_completed())

    def test_exports(self):
        """Test parameter and result exports are OK."""
        # Get rid of weird formatting included in class attribute
        self.maxDiff = 5_000
        self.assertEqual(
            self._meta.to_json().replace("\n", "").replace(" ", ""),
            self._META_MODEL_JSON.replace("\n", "").replace(" ", ""),
        )
        # Test Risk Table
        param_dict = json.loads(self._META_MODEL_JSON)
        del param_dict["creation_date"]
        del param_dict["model_uuid"]
        del param_dict["name"]
        del param_dict["type"]
        self.assertEqual(self._meta.export_params(), param_dict)


if __name__ == "__main__":
    unittest.main()
