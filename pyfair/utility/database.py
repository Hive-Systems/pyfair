import pathlib
import sqlite3

import pandas as pd

#from . import FairException
from pyfair.utility.fair_exception import FairException


class FairDatabase(object):
    '''A wrapper class for an SQLite3 database for storing models.'''
    
    def __init__(self, path):
        self._path = pathlib.Path(path)
        self._initialize()
    
    def _initialize(self):
        '''Initialize if necessary.'''
        with sqlite3.connect(self._path) as conn:
            conn.execute('''CREATE TABLE IF NOT EXISTS pert (uuid string, target string, low real NOT NULL, mode real NOT NULL, high real NOT NULL, gamma real, CONSTRAINT pert_pk PRIMARY KEY (uuid, target));''')
            conn.execute('''CREATE TABLE IF NOT EXISTS bernoulli (uuid string, target string, p real NOT NULL, CONSTRAINT bernoulli_pk PRIMARY KEY (uuid, target));''')
            conn.execute('''CREATE TABLE IF NOT EXISTS constant (uuid stringy, target string, constant real NOT NULL, CONSTRAINT constant_pk PRIMARY KEY (uuid, target));''')
            conn.execute('''CREATE TABLE IF NOT EXISTS normal (uuid string, target string, mean real NOT NULL, stdev real NOT NULL, CONSTRAINT normal_pk PRIMARY KEY (uuid, target));''')
            conn.execute('''CREATE TABLE IF NOT EXISTS secondary (uuid string, name string, frequency real NOT NULL, magnitude real NOT NULL, CONSTRAINT secondary_pk PRIMARY KEY (uuid, name));''')
            conn.execute('''CREATE TABLE IF NOT EXISTS model (uuid string, name string, n_simulations real NOT NULL, creation_date text NOT NULL, random_seed integer NOT NULL, type string NOT NULL, CONSTRAINT model_pk PRIMARY KEY (uuid));''')
            conn.execute('''CREATE TABLE IF NOT EXISTS results (uuid string, mean real NOT NULL, stdev real NOT NULL, min real NOT NULL, max real NOT NULL, CONSTRAINT results_pk PRIMARY KEY (uuid));''')
            conn.execute('''CREATE TABLE IF NOT EXISTS metamodel (id integer, metamodel string NOT NULL, model string NOT NULL, CONSTRAINT metamodel_pk PRIMARY KEY (id));''')

    def load(self, name_or_uuid):
        '''Take a name or UUID and dispatch to appropriate function'''
        # If it is a valid UUID
        try:
            uuid.UUID(name_or_uuid)
            model_or_metamodel = self._load_uuid(name_or_uuid)
        # If not a valid UUID, load by name
        except ValueError:
            model_or_metamodel = self._load_uuid(name_or_uuid)
        return model_or_metamodel
    
    def _load_name(self, name):
        '''Load model or metamodel based on first item with that name.'''
        pass
    
    def _load_uuid(self, uuid):
        '''Load model or metamodel based on ID'''
        pass
    
    def store(self, model_or_metamodel):
        '''Take a model or metamodel and dispatch to appropriate function'''
        class_name = model_or_metamodel.__class__.__name__
        # FairModels go to self._store_model()
        if class_name == 'FairModel':
            self._store_model(model_or_metamodel)
        # FairMetaMOdels go to self._store_metamodel()
        if class_name == 'FairMetaModel':
            self._store_metamodel(model_or_metamodel)
    
    def _store_model(self, model):
        '''Store model'''
        # If incomplete and not ready for storage, throw error
        if not model.calculation_completed():
            raise FairException('Model has not been calculated and will not be stored.')
        # Export from model
        meta = json.loads(model.to_json())
        params = model.export_params()
        results = model.export_results()['Risk']
        # Write to database
        with sqlite3.connect(self._path) as conn:
            cursor = conn.cursor()
            # Write model data
            cursor.execute(
                '''INSERT OR REPLACE INTO model VALUES(?, ?, ?, ?, ?, ?)''',
                (meta['model_uuid'], meta['name'], meta['n_simulations'], meta['creation_date'], meta['random_seed'], meta['type'],)
            )
            # Write cached results
            cursor.execute(
                '''INSERT OR REPLACE INTO results VALUES(?, ?, ?, ?, ?)''',
                (meta['model_uuid'], results.mean(axis=0), results.std(axis=0), results.min(axis=0), results.max(axis=0))
            )
            # Writer pert items
            pert_params      = {key: value for key, value in params.items() if 'low' in value.keys()}
            for target, param_dict in pert_params.items():
                print(target)
                cursor.execute(
                    '''INSERT OR REPLACE INTO pert VALUES(?, ?, ?, ?, ?, ?)''',
                    (meta['model_uuid'], target, param_dict['low'], param_dict['mode'], param_dict['high'], param_dict['gamma'])
                )
            # Writer Bernoulli items
            bernoulli_params = {key: value for key, value in params.items() if 'p' in value.keys()}
            for target, param_dict in bernoulli_params.items():
                cursor.execute(
                    '''INSERT OR REPLACE INTO bernoulli VALUES(?, ?, ?)''',
                    (meta['model_uuid'], target, param_dict['p'])
                )
            # Normal params
            normal_params = {key: value for key, value in params.items() if 'mean' in value.keys()}
            for target, param_dict in normal_params.items():
                cursor.execute(
                    '''INSERT OR REPLACE INTO pert VALUES(?, ?, ?, ?)''',
                    (meta['model_uuid'], target, param_dict['mean'], param_dict['stdev'])
                )
                
            # REMOVE ME
            print(cursor.execute('SELECT * FROM pert;').fetchall())
            # Vacuum database
            conn.execute("VACUUM")
        
    def _store_metamodel(self, metamodel):
        params = metamodel.export_params()
    
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
    
   