"""This module contains a database class for storing models."""

import json
import pathlib
import sqlite3
import uuid

import pandas as pd

from .fair_exception import FairException

from ..model.meta_model import FairMetaModel
from ..model.model import FairModel


class FairDatabase(object):
    """A JSON database antipattern used to store models

    This class is a simple wrapper around an SQLite3 database. It takes a
    path and writes the appropriate tables if necessary. It then allows a
    user to store and load models based on name/uuid, and also allows a
    user to query the contents of that database.

    Parameters
    ----------
    path : str or pathlib.Path
        The path to the database to create or use

    Examples
    --------
    >>> db1 = FairDatabase('/existing/database.sqlite3')
    >>> model = db2.load('Existing Model')
    >>> db2 = FairDatabase('/not/existing/database.sqlite3')
    >>> db2.store(model)
    >>> query_output_string = db2.query('SELECT uuid, json FROM model')

    """
    def __init__(self, path):
        self._path = pathlib.Path(path)
        self._initialize()

    def _initialize(self):
        """Initialize database with tables if necessary."""
        with sqlite3.connect(self._path) as conn:
            conn.execute("""CREATE TABLE IF NOT EXISTS models (
                uuid string,
                name string,
                creation_date text NOT NULL,
                json string NOT NULL,
                CONSTRAINT model_pk PRIMARY KEY (uuid));
            """)
            conn.execute("""CREATE TABLE IF NOT EXISTS results (
                uuid string,
                mean real NOT NULL,
                stdev real NOT NULL,
                min real NOT NULL,
                max real NOT NULL,
                CONSTRAINT results_pk PRIMARY KEY (uuid));
            """)

    def _dict_factory(self, cursor, row):
        """Convenience function for sqlite queries"""
        # https://stackoverflow.com/questions/3300464/
        d = {}
        for idx, col in enumerate(cursor.description):
            d[col[0]] = row[idx]
        return d

    def load(self, name_or_uuid):
        """Loads a model from the database

        This takes a name or UUID and looks up the model using a UUID
        function using self._load_uuid(). If that fails, it attempts to
        look of the funciton by name using self._load_name().

        Parameters
        ----------
        name_or_uuid : str
            The name model or its UUID string

        Returns
        -------
        FairModel or FairMetaModel
            The model or metamodel corresponding with the input UUID string
            or input name string.

        Raises
        ------
        FairException
            When the UUID or name does not exist in the database

        """
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
        """Load model or metamodel based on first item with that name."""
        with sqlite3.connect(self._path) as conn:
            # Create SQlite fow factory
            conn.row_factory = self._dict_factory
            cursor = conn.cursor()
            # Search for models
            cursor.execute("SELECT uuid FROM models WHERE name = ?", (name,))
            result = cursor.fetchone()
            if not result:
                raise FairException('Name for model not found.')
            # Use model UUID query to load via _load_uuid function
            model = self._load_uuid(result['uuid'])
            return model

    def _load_uuid(self, uuid):
        """Load model or metamodel based on ID"""
        # Get models and metamodels
        with sqlite3.connect(self._path) as conn:
            conn.row_factory = self._dict_factory
            cursor = conn.cursor()
            # Search for models
            cursor.execute("SELECT * FROM models WHERE uuid = ?", (uuid,))
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
        """Store a model or metamodel in the database

        Thie function takes a model or metamodel, checks whether the
        appropriate calculations have been completed, and then stores that
        model. The data is stored in two tables: 1) first the aggregate
        statistics about the risk are stored in the 'results' table, and 2)
        the model data is stored in the 'models' table.

        Raises
        ------
        FairException
            If model or metamodel is not yet calculated

        """
        m = model_or_metamodel
        # If incomplete and not ready for storage, throw error
        if not m.calculation_completed():
            raise FairException("Model is uncalculated and won't be stored.")
        # Export from model
        meta = json.loads(m.to_json())
        json_data = m.to_json()
        results = m.export_results()['Risk']
        # Write to database
        with sqlite3.connect(self._path) as conn:
            cursor = conn.cursor()
            # Write model data
            cursor.execute(
                """INSERT OR REPLACE INTO models VALUES(?, ?, ?, ?)""",
                (
                    meta['model_uuid'], 
                    meta['name'], 
                    meta['creation_date'], 
                    json_data
                )
            )
            # Write cached results
            cursor.execute(
                """INSERT OR REPLACE INTO results VALUES(?, ?, ?, ?, ?)""",
                (
                    meta['model_uuid'], 
                    results.mean(axis=0),
                    results.std(axis=0),
                    results.min(axis=0),
                    results.max(axis=0)
                )
            )
        # Vacuum database
        conn = sqlite3.connect(self._path)
        conn.execute("VACUUM")
        conn.commit()
        conn.close()

    def query(self, query, params=None):
        """Function for querying the underlying database.

        Parameters
        ----------
        query : str
            The base SQL for a query or parameterized query

        params : tuple, optional
            Params for any parameterized queries. The content can vary
            based on sqlite3 conversion rules.

        Returns
        -------
        list of sqlite3.Row objects
            The raw query result from fetchall()

        """
        with sqlite3.connect(self._path) as conn:
            cursor = conn.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            result = cursor.fetchall()
        return result
