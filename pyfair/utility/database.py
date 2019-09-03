import json
import pathlib
import sqlite3
import uuid

import pandas as pd

from .fair_exception import FairException

from ..model.meta_model import FairMetaModel
from ..model.model import FairModel


class FairDatabase(object):
    '''JSON database antipattern.'''

    def __init__(self, path):
        self._path = pathlib.Path(path)
        self._initialize()

    def _initialize(self):
        '''Initialize if necessary.'''
        with sqlite3.connect(self._path) as conn:
            conn.execute('''CREATE TABLE IF NOT EXISTS model (uuid string, 
                                                              name string, 
                                                              creation_date text NOT NULL,
                                                              json string NOT NULL,
                                                              CONSTRAINT model_pk PRIMARY KEY (uuid));''')
            conn.execute('''CREATE TABLE IF NOT EXISTS results (uuid string,
                                                                mean real NOT NULL, 
                                                                stdev real NOT NULL, 
                                                                min real NOT NULL, 
                                                                max real NOT NULL, 
                                                                CONSTRAINT results_pk PRIMARY KEY (uuid));''')
    
    def _dict_factory(self, cursor, row):
        '''Convenience function for sqlite'''
        # https://stackoverflow.com/questions/3300464/how-can-i-get-dict-from-sqlite-query
        d = {}
        for idx, col in enumerate(cursor.description):
            d[col[0]] = row[idx]
        return d

    def load(self, name_or_uuid):
        '''Take a name or UUID and dispatch to appropriate function'''
        # If it is a valid UUID
        try:
            uuid.UUID(name_or_uuid)
            model_or_metamodel = self._load_uuid(name_or_uuid)
        # If not a valid UUID, load by name
        except ValueError:
            model_or_metamodel = self._load_name(name_or_uuid)
        model_or_metamodel.calculate_all()
        return model_or_metamodel
    
    def _load_name(self, name):
        '''Load model or metamodel based on first item with that name.'''
        with sqlite3.connect(self._path) as conn:
            # Create SQlite fow factory
            conn.row_factory = self._dict_factory
            cursor = conn.cursor()
            # Search for models
            cursor.execute("SELECT uuid FROM model WHERE name = ?", (name,))
            result = cursor.fetchone()
            if not result:
                raise FairException('Name for model not found.')
            # Use model UUID query to load via _load_uuid function
            model = self._load_uuid(result['uuid'])
            return model

    def _load_uuid(self, uuid):
        '''Load model or metamodel based on ID'''
        # Get models and metamodels
        with sqlite3.connect(self._path) as conn:
            conn.row_factory = self._dict_factory
            cursor = conn.cursor()
            # Search for models
            cursor.execute("SELECT * FROM model WHERE uuid = ?", (uuid,))
            model_data = cursor.fetchone()
            if not model_data:
                raise FairException('UUID for model not found.')
            # Load model type based on json
            json_data = model_data['json']
            model_param_data = json.loads(json_data)
            model_type = model_param_data['type']
            if model_type == 'FairMetaModel':
                model = FairMetaModel.read_json(json_data)
            elif model_type == 'FairModel':
                model = FairModel.read_json(json_data)
            else:
                raise FairException('Unrecognized model type.')
        return model

    def store(self, model_or_metamodel):
        '''Take a model or metamodel and store in db'''
        m = model_or_metamodel
        # If incomplete and not ready for storage, throw error
        if not m.calculation_completed():
            raise FairException('Model has not been calculated and will not be stored.')
        # Export from model
        meta = json.loads(m.to_json())
        json_data = m.to_json()
        results = m.export_results()['Risk']
        # Write to database
        with sqlite3.connect(self._path) as conn:
            cursor = conn.cursor()
            # Write model data
            cursor.execute(
                '''INSERT OR REPLACE INTO model VALUES(?, ?, ?, ?)''',
                (meta['model_uuid'], meta['name'], meta['creation_date'], json_data)
            )
            # Write cached results
            cursor.execute(
                '''INSERT OR REPLACE INTO results VALUES(?, ?, ?, ?, ?)''',
                (meta['model_uuid'], results.mean(axis=0), results.std(axis=0), results.min(axis=0), results.max(axis=0))
            )
        # Vacuum database
        conn = sqlite3.connect(self._path)
        conn.execute("VACUUM")
        conn.commit()
        conn.close()

    def query(self, query, params=None):
        '''Allow queries on underlying database'''
        with sqlite3.connect(self._path) as conn:
            cursor = conn.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            result = cursor.fetchall()
        return result
