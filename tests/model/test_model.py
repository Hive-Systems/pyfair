import unittest

from .. import context

from pyfair.model.model import FairModel
from pyfair.utility.fair_exception import FairException


class TestFairModel(unittest.TestCase):

    MODEL_TABLE_COLUMN_COUNT = 13

    def test_creation(self):
        '''Test basic instantiation.'''
        # Create FairModel
        model = FairModel('Test', 100, random_seed=42)
        # Ensure existence of appropriate attributes
        self.assertTrue(model._tree)
        self.assertTrue(model._data_input)
        self.assertTrue(model._calculation)
        self.assertTrue(model._model_uuid)
        self.assertTrue(model._creation_date)
        # Check that the table is of proper
        self.assertEqual(len(model._model_table.columns), self.MODEL_TABLE_COLUMN_COUNT)

    def test_read_json(self):
        '''Test static method for reading JSON'''
        # Get JSON
        model_json_path = context.data_directory / 'serialized_model.json'
        metamodel_json_path = context.data_directory / 'serialized_metamodel.json'
        model_json_string = model_json_path.read_text()
        metamodel_json_string = metamodel_json_path.read_text()
        # Instantiate model
        model = FairModel.read_json(model_json_string)
        self.assertTrue(model)
        # Ensure metamodel fails
        self.assertRaises(FairException, FairModel.read_json, metamodel_json_string)

    def test_inputs(self):
        pass

    def test_calculation(self):
        pass

    def test_exports(self):
        pass

if __name__ == '__main__':
    unittest.main()