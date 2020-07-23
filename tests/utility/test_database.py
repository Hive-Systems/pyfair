import pathlib
import unittest

from pyfair.model.meta_model import FairMetaModel
from pyfair.model.model import FairModel
from pyfair.utility.database import FairDatabase
from pyfair.utility.fair_exception import FairException


class TestFairDatabase(unittest.TestCase):

    _BULK_IMPORT_DATA = {
        'Primary Loss': {"mean": 5_000_000, "stdev": 10},
        'Secondary Loss': {"constant": 100},
        'Loss Event Frequency': {"low": 0, "most_likely": 80, "high": 100},
        'Threat Capability': {"low": 0, "most_likely": .4, "high": .9, "gamma": 3},
        'Control Strength': {"low": .3, "most_likely": .4, "high": .5},
    }
    _QUERY_STRING = """
        SELECT 
            *
        FROM 
            models
        LEFT JOIN 
            results
        ON
            models.uuid=results.uuid
        WHERE
            models.uuid=?

    """

    def setUp(self):
        # sqlite does not seem to like tempfile
        self._tf = pathlib.Path().home() / 'pyfair_test.sqlite'
        self._db = FairDatabase(str(self._tf))

    def tearDown(self):
        self._tf.unlink()
        self._tf = None
        self._db = None

    def test_all_database_methods(self):
        """Test all database methods"""
        # This is based on state and not well-suited to unit tests
        model = FairModel('model')
        model.bulk_import_data(self._BULK_IMPORT_DATA)
        # Check uncalcualted models throw errors (metamodel always calc'd)
        self.assertRaises(FairException, self._db.store, model)
        model = FairModel('model')
        model.bulk_import_data(self._BULK_IMPORT_DATA)
        model.calculate_all()
        # All argument and model types
        metamodel = FairMetaModel('meta', models=[model, model])
        metamodel.calculate_all()
        # Things to fetch from db
        model_name = model.get_name()
        model_uuid = model.get_uuid()
        meta_model_name = metamodel.get_name()
        meta_model_uuid = metamodel.get_uuid()
        load_strings = [
            model_name, 
            model_uuid, 
            meta_model_name, 
            meta_model_uuid
        ]
        # Store
        for m in [model, metamodel]:
            self._db.store(m)
        # For load via all stirngs
        for string in load_strings:
            _ = self._db.load(string)
        # Confirm query is working
        result = self._db.query(
            self._QUERY_STRING,
            (model_uuid,)
        )
        self.assertTrue(len(result) == 1)


if __name__ == '__main__':
    unittest.main()