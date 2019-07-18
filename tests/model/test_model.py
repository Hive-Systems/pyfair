import json
import pathlib
import unittest

import pandas as pd

from pyfair.model.model import FairModel
from pyfair.utility.fair_exception import FairException


class TestFairModel(unittest.TestCase):

    MODEL_TABLE_COLUMN_COUNT = 13
    N_SAMPLES = 100
    MODEL_JSON = '{     "Loss Event Frequency": {         "low": 20,         "mode": 100,         "high": 900     },     "Loss Magnitude": {         "low": 3000000,         "mode": 3500000,         "high": 5000000     },     "name": "Regular Model 1",     "n_simulations": 10000,     "random_seed": 42,     "model_uuid": "b6c6c968-a03c-11e9-a5db-f26e0bbd6dbc",     "type": "FairModel",     "creation_date": "2019-07-06 17:23:43.647370" }'
    META_MODEL_JSON = '{     "Regular Model 1": {         "Loss Event Frequency": {             "low": 20,             "mode": 100,             "high": 900         },         "Loss Magnitude": {             "low": 3000000,             "mode": 3500000,             "high": 5000000         },         "name": "Regular Model 1",         "n_simulations": 10000,         "random_seed": 42,         "model_uuid": "b6c6c968-a03c-11e9-a5db-f26e0bbd6dbc",         "type": "FairModel",         "creation_date": "2019-07-06 17:23:43.647370"     },     "Regular Model 2": {         "Loss Event Frequency": {             "mean": 0.3,             "stdev": 0.1         },         "Loss Magnitude": {             "low": 2000000000,             "mode": 3000000000,             "high": 5000000000         },         "name": "Regular Model 2",         "n_simulations": 10000,         "random_seed": 42,         "model_uuid": "b6ca98a4-a03c-11e9-8ce0-f26e0bbd6dbc",         "type": "FairModel",         "creation_date": "2019-07-06 17:23:43.672336"     },     "name": "My Meta Model!",     "model_uuid": "b6cce298-a03c-11e9-b79f-f26e0bbd6dbc",     "creation_date": "2019-07-06 17:23:43.687336",     "type": "FairMetaModel" }'

    def test_creation(self):
        '''Test basic instantiation.'''
        # Create FairModel
        model = FairModel('Test', self.N_SAMPLES, random_seed=42)
        # Ensure existence of appropriate attributes
        attributes = [
            model._tree,
            model._data_input,
            model._calculation,
            model._model_uuid,
            model._creation_date,
        ]
        for attribute in attributes:
            self.assertTrue(attribute)

        # Check that the table is of proper
        self.assertEqual(len(model._model_table.columns), self.MODEL_TABLE_COLUMN_COUNT)

    def test_read_json(self):
        '''Test static method for reading JSON'''
        # Instantiate model
        model = FairModel.read_json(self.MODEL_JSON)
        self.assertTrue(model)
        # Ensure metamodel fails
        self.assertRaises(FairException, FairModel.read_json, self.META_MODEL_JSON)

    def test_inspection(self):
        '''Check the inspection methods'''
        # Build model
        model = FairModel('Test', self.N_SAMPLES)
        model.input_data('Loss Magnitude', mean=20, stdev=10)
        model.input_data('Loss Event Frequency', constant=10)
        model.input_data('Loss Magnitude', constant=10)
        model.calculate_all()
        # Check inspection methods
        model.get_node_statuses()
        model.get_name()
        model.calculation_completed()

    def test_inputs(self):
        '''Check the input methods (leave validation to FairDataInput)'''
        # Test basic input
        model = FairModel('Test', self.N_SAMPLES)
        model.input_data('Loss Magnitude', constant=100)
        # Test duplicate inputs passed
        model.input_data('Loss Magnitude', constant=10)
        # Test bulk_import_data
        model.bulk_import_data({
            'Loss Magnitude': {'constant': 100},
            'Loss Event Frequency': {'low': 10, 'mode': 15, 'high': 20}
        })
        # Test import_multi_data
        model.input_multi_data('Secondary Loss', {
            'Reputational': {
                'Secondary Loss Event Frequency': {'constant': 4000}, 
                'Secondary Loss Event Magnitude': {'low': 10, 'mode': 20, 'high': 100},
            },
            'Legal': {
                'Secondary Loss Event Frequency': {'constant': 2000}, 
                'Secondary Loss Event Magnitude': {'low': 10, 'mode': 20, 'high': 100},        
            }
        })

    def test_calculation(self):
        '''Run a calulate all.'''
        # Create model and import data
        model = FairModel('Test', self.N_SAMPLES)
        model.input_data('Loss Magnitude', constant=100)
        # Calculate based on incomplete data
        self.assertRaises(FairException, model.calculate_all)
        # Complete calculation and run
        model.input_data('Loss Event Frequency', constant=10)
        model.calculate_all()

    def test_exports(self):
        '''Test outputs post calculation'''
        # Create model and calculate
        model = FairModel('Test', self.N_SAMPLES)
        model.bulk_import_data({
            'Loss Magnitude': {'constant': 100},
            'Loss Event Frequency': {'low': 10, 'mode': 15, 'high': 20}
        })
        model.calculate_all()
        # Export results
        results = model.export_results()
        self.assertIsInstance(results, pd.DataFrame)
        self.assertTrue(len(results) == self.N_SAMPLES)        
        # Export json and ensure parse-able
        json_data = model.to_json()
        self.assertIsInstance(json_data, str)
        _ = json.loads(json_data)
        # Export params
        params = model.export_params()
        self.assertIsInstance(params, dict)
        self.assertTrue(params)


if __name__ == '__main__':
    unittest.main()