import datetime
import json
import uuid

import pandas as pd

from ..utility import FairException

from .model import FairModel


class FairMetaModel(object):
    '''An aggregation of models used to add up risk.'''
    # TODO should 'meta_model_uuid' just be 'model_uuid'?

    def __init__(self, name=None, models=None, meta_model_uuid=None):
        self._name = name
        self._params = {}
        self._risk_table = pd.DataFrame()
        # For every model, flatten and save params.
        for model in models:
            # If model, load
            if type(model) == FairModel:
                self._load_model(model)
            # If metamodel, load components.
            if type(model) == type(self):
                self._load_meta_model(model)
        # Assign UUID
        if meta_model_uuid:
            self._meta_model_uuid = meta_model_uuid
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
        # Get model params
        model_params = {
            key: value
            for key, value
            in data.items()
            if key not in ['name', 'model_uuid', 'type']
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
            meta_model_uuid=data['model_uuid']
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
            if key not in ['name', 'model_uuid', 'type']
        }
        # Iterate through params
        for model_params in params.values():
            # If model, load model from json and load into meta
            model_json = json.dumps(model_params)
            model = FairModel.read_json(model_json)
            self._load_model(model)

    def _record_params(self, model):
        model_params = model.export_params()
        model_json = json.loads(model.to_json())
        model_name = model_json['name']
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
