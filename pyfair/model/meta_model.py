import json
import uuid

import pandas as pd


class FairMetaModel(object):
    '''A collection of models.'''

    def __init__(self, name=None, models=None, meta_model_uuid=None):
        self._name = name
        self._params = {}
        self._risk_table = pd.DataFrame()
        # For every model, flatten and save params.
        for model in models:
            self._record_params(model)
            self._calculate_model(model)
        # UUID
        if meta_model_uuid:
            self._meta_model_uuid = meta_model_uuid
        else:
            self._meta_model_uuid = str(uuid.uuid1())

    @staticmethod
    def read_json(data):
        pass

    def _record_params(self, model):
        model_params = model.export_params()
        model_json = json.loads(model.to_json())
        model_name = model_json['name']
        self._params[model_name] = model_params
    
    def _calculate_model(self, model):
        # For each model, calculate and put output results in dataframe.
        params = model.export_params()
        model_json = json.loads(model.to_json())
        name = model_json['name']
        model.calculate_all()
        results = model.export_results()
        self._risk_table[name] = results['Risk']

    def export_params(self):
        return self._params

    def calculate_all(self):
        sum_vector = self._risk_table.sum(axis=0)
        self._risk_table['Risk'] = sum_vector

    def export_results(self):
        return self._risk_table
    
    def to_json(self):
        data = {**self._params}
        data['name'] = str(self._name)
        data['meta_model_uuid'] = self._meta_model_uuid
        data['type'] = str(self.__class__)
        json_data = json.dumps(
            data,
            indent=4,
        )
        return json_data
