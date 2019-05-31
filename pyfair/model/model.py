import json
import uuid

import numpy as np
import pandas as pd

from .model_input import FairDataInput
from .model_tree import FairDependencyTree
from .model_calc import FairCalculations
from ..utility.fair_exception import FairException


class FairModel(object):
    '''A main class to act as an API for FAIR Model construction.'''
    
    # TODO confirm mapping names to ensure they are consistent with current nomenclature
    def __init__(self, name, n_simulations=10_000, random_seed=42, model_uuid=None):
        # Set n_simulations and random seed for reproducablility
        self._name = name
        self._n_simulations = n_simulations
        # Do not change the random_seed unless you have a good reason.
        self._random_seed = random_seed
        np.random.seed(random_seed)
        # Instantiate components
        self._model_table  = pd.DataFrame(columns=[
            'Risk', 
            'Loss Event Frequency',
            'Threat Event Frequency', 
            'Vulnerability', 
            'Contact', 
            'Action', 
            'Threat Capability', 
            'Control Strength', 
            'Probable Loss Magnitude', 
            'Primary Loss Factors', 
            'Asset Loss Factors',
            'Threat Loss Factors',
            'Secondary Loss Factors',
            'Organizational Loss Factors', 
            'External Loss Factors'
        ])
        self._data_input  = FairDataInput() 
        self._tree        = FairDependencyTree()
        self._calculation = FairCalculations()
        # If no ID supplied, create.
        if model_uuid:
            self._model_uuid  = model_uuid
        else:
            self._model_uuid = str(uuid.uuid1())
            self._creation_date = str(pd.datetime.now())

    def get_uuid(self):
        return self._model_uuid

    @staticmethod
    def read_json(param_json):
        '''Class function for loading a model from json'''
        data = json.loads(param_json)
        # TODO CHeck for metamodel or model
        model = FairModel(
            data['name'],
            data['n_simulations'], 
            data['random_seed'],
            data['model_uuid']
        )
        # Be lazy
        for key in ['name',
                    'n_simulations', 
                    'random_seed', 
                    'Creation Datetime', 
                    'model_uuid',
                    'type']:
            del data[key]
        # Load params one-by-one.
        for param_name, param_value in data.items():
            model.input_data(param_name, **param_value)
        # Calculate
        model.calculate_all()
        return model

    def get_node_statuses(self):
        '''Public method to give access to internals'''
        return self._tree.get_node_statuses()

    def input_data(self, target, **kwargs):
        data = self._data_input.generate(target, self._n_simulations, **kwargs)
        self._tree.update_status(target, 'Supplied')
        self._model_table[target] = data
        return self

    def bulk_import_data(self, param_dictionary):
        '''This takes {'target': {param_1: value_1}} formatted dictionaries'''
        for target, parameters in param_dictionary.items():
            self.input_data(target, **parameters)
        return self
        
    def calculate_all(self):
        '''Calculate all nodes'''
        # If required data has not been input, raise error
        ready_for_calculation = self._tree.ready_for_calculation()
        if not(ready_for_calculation):
            status_str = str(pd.Series(self._tree.get_node_statuses()))
            raise FairException('Not ready for calculation. See statuses: \n{}'.format(status_str))
        status = pd.Series(self._tree.get_node_statuses())
        calculable_nodes = status[status == 'Calculable'].index.values.tolist()
        # Go through all the nodes and update them if possible.
        while calculable_nodes:
            # Avoid mutating while iterating.
            node_names = tuple(calculable_nodes)
            for node_name in node_names:
                # Calculate if possible
                self._calculate_node(node_name)
                # Remove node from list if calculated.
                if self._tree.nodes[node_name].status == 'Calculated':
                    calculable_nodes.remove(node_name)
        return self
    
    def _calculate_node(self, name):
        '''Calculate an individual node'''
        # Alsias for data table
        data = self._model_table
        # Get child node statuses
        parent = self._tree.nodes[name]
        child_1, child_2 = parent.children
        child_1_ready = child_1.status in ['Calculated', 'Supplied']
        child_2_ready = child_2.status in ['Calculated', 'Supplied']
        # If children ready for calculation, calculate
        if child_1_ready and child_2_ready:
            # Order for vulnerability matters.
            if parent.name == 'Vulnerability':
                child_1_data = data['Control Strength']
                child_2_data = data['Threat Capability']
            # For others, it matters not.
            else:
                child_1_data = data[child_1.name]
                child_2_data = data[child_2.name]
            calculated_data = self._calculation.calculate(name, child_1_data, child_2_data)
            data[name] = calculated_data
            self._tree.update_status(name, 'Calculated')
        else:
            pass

    def export_results(self):
        return self._model_table

    def to_json(self):
        '''Dump model as json'''
        data = self._data_input.get_supplied_values()
        data['name'] = str(self._name)
        data['n_simulations'] = self._n_simulations
        data['random_seed'] = self._random_seed
        data['model_uuid'] = self._model_uuid
        data['type'] = str(self.__class__.__name__)
        data['creation_date'] = self._creation_date
        json_data = json.dumps(
            data,
            indent=4,
        )
        return json_data

    def export_params(self):
        '''Export params as dict'''
        # <screed>
        #    I know. I know. Getters and setters have no place in Python.
        #    That said ... if it's public people will read AND write it.
        #    We definitely don't want people writing to params.
        #    We could wrap a decorator allowing setting, but that's overkill.
        #    It's better to just have a simple export function.
        # </screed>
        return self._data_input.get_supplied_values()

    def get_name(self):
        return self._name
