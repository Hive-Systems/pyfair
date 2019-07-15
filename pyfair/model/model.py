import json
import uuid

import numpy as np
import pandas as pd

from .model_input import FairDataInput
from .model_tree import FairDependencyTree
from .model_calc import FairCalculations
from ..utility.fair_exception import FairException


class FairModel(object):
    """A main class to act as an API for FAIR Model construction.
    
    Attributes
    ----------
    _name : str
        A human-readable designation for identification
    _n_simulations : int
        The number of Monte Carlo simulations being created

    """
    
    def __init__(self, name, n_simulations=10_000, random_seed=42, model_uuid=None, creation_date=None):
        """
            .. warning:: Do not supply your own UUID/creation date unless you want to break things.

        """
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
            'Loss Magnitude', 
            'Primary Loss', 
            'Secondary Loss',
            'Secondary Loss Event Frequency', 
            'Secondary Loss Event Magnitude',
        ])
        self._data_input  = FairDataInput() 
        self._tree        = FairDependencyTree()
        self._calculation = FairCalculations()
        # If no ID supplied, create.
        if model_uuid and creation_date:
            self._model_uuid  = model_uuid
            self._creation_date = creation_date
        else:
            self._model_uuid = str(uuid.uuid1())
            self._creation_date = str(pd.datetime.now())

    @staticmethod
    def read_json(param_json):
        '''Class function for loading a model from json'''
        data = json.loads(param_json)
        # Check type of JSON
        if data['type'] != 'FairModel':
            raise FairException('Failed JSON parse attempt. This is not a FairModel.')
        model = FairModel(
            name=data['name'],
            n_simulations=data['n_simulations'], 
            random_seed=data['random_seed'],
            model_uuid=data['model_uuid'],
            creation_date=data['creation_date']
        )
        # Be lazy
        drop_params = [
            'name',
            'n_simulations', 
            'random_seed', 
            'creation_date', 
            'model_uuid',
            'type'
        ]
        # Load params one-by-one.
        for param_name, param_value in data.items():
            # If it's not in the drop list, load it.
            if param_name not in drop_params:
                if param_name.startswith('multi'):
                    model.input_multi_data(param_name, param_value)
                else:
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

    def input_multi_data(self, target, kwargs_dict):
        data = self._data_input.generate_multi(target, self._n_simulations, kwargs_dict)
        # Supplied then calculated is a nasty workaround to propegate down then change.
        mod_target = target.lstrip('multi_')
        self._tree.update_status(mod_target, 'Supplied')
        self._tree.update_status(mod_target, 'Calculated')
        self._model_table[mod_target] = data
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
        # Copy only.
        data = {**self._data_input.get_supplied_values()}
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
    
    def calculation_completed(self):
        '''Check tree to see if the dependencies are complete'''
        status = self._tree.calculation_completed()
        return status
