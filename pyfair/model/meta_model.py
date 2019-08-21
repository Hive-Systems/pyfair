"""This module contains a class for creating composite FAIR models."""

import datetime
import json
import uuid

import pandas as pd

from ..utility import FairException

from .model import FairModel


class FairMetaModel(object):
    """A class for aggregating FAIR models.
    
    An instance of this class is created by taking multiple FAIR models and
    rolling the total risk into a collection, or MetaModel. A user creates
    a metamodel from inputs, calls calculate_all() to perform the requisite
    calculations, and then uses the metamodel for reporting.

    Parameters
    ----------
    name : str
        A human-readable designation for identification
    models : list of FairModels
        The sub-models that roll up into the aggregate MetaModel risk
        calculation.
    model_uuid : str, optional
        uuid.uuid4 string (default is None, meaning one will be assigned)
    creation_date : str, optional
        Creation date (default is None, meaning one will be assigned)

    Examples
    --------
    >>> m1 = pyfair.model.FairModel.from_json('model_1.json')
    >>> m2 = pyfair.model.FairModel.from_json('model_2.json')
    >>> meta1  = pyfair.model.FairMetaModel('Name', [m1, m2])
    >>> meta1.calculate_all()
    >>> meta1.export_results()

    .. warning:: Do not supply your own UUID/creation date unless you
        want to break things.

    """

    def __init__(self, name=None, models=None, model_uuid=None, creation_date=None):
        self._name = name
        self._params = {}
        self._risk_table = pd.DataFrame()
        # For every model, flatten and save params.
        for model in models:
            # If model, load
            if type(model) == FairModel:
                self._load_model(model)
            # If metamodel, load components.
            elif type(model) == type(self):
                self._load_meta_model(model)
            else:
                err = f'Input {model} is not a FairModel or FairMetaModel.'
                raise FairException(err)
        # Assign UUID
        if model_uuid and creation_date:
            self._model_uuid = model_uuid
            self._creation_date = creation_date
        else:
            self._model_uuid = str(uuid.uuid1())
            self._creation_date = str(datetime.datetime.now())

    def get_name(self):
        return self._name

    def get_uuid(self):
        return self._model_uuid

    @staticmethod
    def read_json(json_data):
        # TODO this is inefficient and convoluted
        # TODO Support metamodels inside of metamodels
        data = json.loads(json_data)
        # Check type of JSON
        if data['type'] != 'FairMetaModel':
            raise FairException('Failed JSON parse attempt. This is not a FairMetaModel.')
        # Get model params
        model_params = {
            key: value
            for key, value
            in data.items()
            if key not in ['name', 'model_uuid', 'type', 'creation_date']
        }
        # Instantiate models (there is no need to cover)
        # metamodels here because metamodel json only
        # has models in it, not metamodels.
        models = [
            FairModel.read_json(json.dumps(value))
            for value
            in model_params.values()
        ]
        # Create metamodel
        meta_model = FairMetaModel(
            name=data['name'],
            models=models,
            model_uuid=data['model_uuid'],
            creation_date=data['creation_date']
        )
        return meta_model
    
    def _load_model(self, model):
        '''Loads an individual model into the metamodel'''
        self._record_params(model)
        self._calculate_model(model)
    
    def _load_meta_model(self, meta_model):
        '''Loads a metamodel into the metamodel'''
        params = meta_model.export_params()
        params = {
            key: value
            for key, value
            in params.items()
            if key not in ['name', 'model_uuid', 'type', 'creation_date']
        }
        # Iterate through params
        for model_params in params.values():
            # If model, load model from json and load into meta
            model_json = json.dumps(model_params)
            model = FairModel.read_json(model_json)
            self._load_model(model)

    def _record_params(self, model):
        model_params = json.loads(model.to_json())
        model_name = model_params['name']
        self._params[model_name] = model_params
    
    def _calculate_model(self, model):
        # For each model, calculate and put output results in dataframe.
        model_json = json.loads(model.to_json())
        name = model_json['name']
        model.calculate_all()
        results = model.export_results()
        self._risk_table[name] = results['Risk']

    def export_params(self):
        return self._params

    def calculate_all(self):
        sum_vector = self._risk_table.sum(axis=1)
        self._risk_table['Risk'] = sum_vector
        # Check for NaN values in sum_vector
        if pd.isnull(sum_vector).any():
            raise FairException('np.NaN values in summed Risk column.' 
                                ' Likely cause: n_simulations mismatch across models.')
        return self

    def export_results(self):
        return self._risk_table
    
    def to_json(self):
        data = {**self._params}
        data['name'] = str(self._name)
        data['model_uuid'] = self._model_uuid
        data['creation_date'] = self._creation_date
        data['type'] = str(self.__class__.__name__)
        json_data = json.dumps(
            data,
            indent=4,
        )
        return json_data

    def calculation_completed(self):
        '''Check if calculations are complete'''
        if 'Risk' in self._risk_table.columns:
            return True
        else:
            return False
