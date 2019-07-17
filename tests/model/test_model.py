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

    def test_inspection(self):
        '''Check the inspection methods'''
        # Build model
        model = FairModel('Test', 100)
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
        model = FairModel('Test', 100)
        model.input_data('Loss Magnitude', constant=100)
        # Test duplicate inputs passed
        model.input_data('Loss Magnitude', constant=10)
        # Test bulk_import_data

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


    def test_dependency_tree(self):
        pass


    def test_calculation(self):
        pass

    def test_exports(self):
        pass

if __name__ == '__main__':
    unittest.main()