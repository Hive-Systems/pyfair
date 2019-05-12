import json
import uuid

import numpy as np
import pandas as pd
import scipy.stats

from .utility import FairException
from .utility import FairBetaPert


class FairModel(object):
    '''A main class to act as an API for FAIR Model construction.'''
    
    def __init__(self, name=None, n_simulations=10_000, random_seed=34, model_uuid=None):
        # Set n_simulations and random seed for reproducablility
        self._name = name
        self._n_simulations = n_simulations
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

    def input_data(self, target, **kwargs):
        data = self._data_input.generate(target, self._n_simulations, **kwargs)
        self._tree.update_status(target, 'Supplied')
        self._model_table[target] = data
        
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
        data['type'] = str(self.__class__)
        json_data = json.dumps(
            data,
            indent=4,
        )
        return json_data

    def export_params(self):
        '''Export params as dict'''
        # <screed>
        # I know. I know. Getters and setters have no place in Python.
        # That said ... if it's people will read AND write it.
        # We definitely don't want people writing to params.
        # We could wrap a decorator allowing setting, but that's overkill.
        # It's better to just have a simple export function.
        # </screed>
        return self._data_input.get_supplied_values()


class FairDependencyNode(object):
    '''Represents the status of a given calculation'''
    
    def __init__(self, name):
        self.name     = name
        self.parent   = None
        self.children = []
        # Statuses: Required, Not Required, Supplied, Calculable, Calculated
        self.status   = 'Required' 
        
    def __repr__(self):
        return 'FairNode({}, Status={})'.format(self.name, self.status)

    def add_child(self, child):
        self.children.append(child)
        child.add_parent(self)
        return self
    
    def add_parent(self, parent):
        self.parent = parent
        return self

    
class FairDependencyTree(object):
    '''Represents status of a tree of calculations.
    
    See also:
        http://pubs.opengroup.org/onlinepubs/9699919899/toc.pdf
    
    '''
    
    def __init__(self):
        # Leaf nodes for reference
        self._leaf_nodes = []
        self._node_statuses = {}
        # Create and add nodes to tree
        self._root = FairDependencyNode('Risk')
        self._node_names = [
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
        ]
        # Initial tree setup
        self.nodes = {
            node_name: FairDependencyNode(node_name)
            for node_name
            in self._node_names
        }
        # Initial tree setup
        self._root = self.nodes['Risk']
        self._link_nodes()
        self._obtain_leaf_nodes(self._root)
    
    def ready_for_calculation(self):
        '''Ensure there are no required items remaining'''
        if 'Required' in self._node_statuses.values():
            return False
        else:
            return True
        
    def update_status(self, node_name, new_status):
        '''Notify node that data was provided'''
        node = self.nodes[node_name]
        if new_status == 'Supplied':
            node.status = 'Supplied'
            # Let child nodes know they are no longer required
            for child_node in node.children:
                self._propogate_down(child_node)
            # Let parent nodes know they should check for their deps
            for node in self._leaf_nodes:
                self._propogate_up(node)
        # Calculated status requires no propogation
        if new_status == 'Calculated':
            node.status = 'Calculated'
        # Update node status dict
        self._obtain_status(self._root)
        
    def get_node_statuses(self):
        return self._node_statuses

    def _link_nodes(self):
        # Node dict alias for brevity
        nodes = self.nodes
        # Add branches to root
        nodes['Risk'].add_child(nodes['Loss Event Frequency'])
        nodes['Risk'].add_child(nodes['Probable Loss Magnitude'])
        # Loss Event Frequency Branch
        nodes['Loss Event Frequency'].add_child(nodes['Threat Event Frequency'])
        nodes['Loss Event Frequency'].add_child(nodes['Vulnerability'])
        # Threat Event Frequency Subbranch
        nodes['Threat Event Frequency'].add_child(nodes['Contact'])
        nodes['Threat Event Frequency'].add_child(nodes['Action'])
        # Vulnerability Subbranch
        nodes['Vulnerability'].add_child(nodes['Control Strength'])
        nodes['Vulnerability'].add_child(nodes['Threat Capability'])
        # Probable Loss Magnitude Branch
        nodes['Probable Loss Magnitude'].add_child(nodes['Primary Loss Factors'])
        nodes['Probable Loss Magnitude'].add_child(nodes['Secondary Loss Factors'])
        # Primary Loss Factors Subbranch
        nodes['Primary Loss Factors'].add_child(nodes['Asset Loss Factors'])
        nodes['Primary Loss Factors'].add_child(nodes['Threat Loss Factors'])
        # Secondary Loss Factors Subbranch
        nodes['Secondary Loss Factors'].add_child(nodes['Organizational Loss Factors'])
        nodes['Secondary Loss Factors'].add_child(nodes['External Loss Factors'])
            
    def _obtain_status(self, node):
        '''Traverse the tree and record the statuses'''
        self._node_statuses[node.name] = node.status 
        for node in node.children:
            self._obtain_status(node)

    def _obtain_leaf_nodes(self, node):
        '''Traverse the tree and record the leaf nodes. Only run once, ideally.'''
        if len(node.children) == 0:
            self._leaf_nodes.append(node)
        for child_node in node.children:
            self._obtain_leaf_nodes(child_node)

    def _propogate_down(self, node):
        '''Update child node status down from root to leaf nodes'''
        # Update node since children and subchildren no longer needed
        node.status = 'Not Required'
        # Recursively call for children
        for child_node in node.children:
            self._propogate_down(child_node)
    
    def _propogate_up(self, node):
        '''Update parent node statuses up to root node'''
        if node.parent:
            parent_node = node.parent
            # If it was Not Required, Supplied, or Calculated, it stays the same
            if parent_node.status in ['Not Required', 'Supplied', 'Calculated', 'Calculable']:
                pass
            # If it is Required, check to see if parent's child nodes now allow for calculation
            # I.E. if all are either 'Calculable', 'Calculated', or 'Supplied'
            elif parent_node.status == 'Required':
                # Get statuses
                statuses = [
                    child_node.status 
                    for child_node 
                    in parent_node.children
                ]
                # Get a bool for each of the statuses
                status_allows_for_calculation = [
                    status in ['Calculable', 'Calculated', 'Supplied']
                    for status
                    in statuses
                ]
                # If all statuses allow for calculation, change parent to "Calculable"
                if all(status_allows_for_calculation):
                    parent_node.status = 'Calculable'
            # Recursively call
            self._propogate_up(node.parent)
        # If no parent, do nothing.
        else:
            pass


class FairDataInput(object):
    '''Data entry and validation.'''
    
    def __init__(self):
        # Lookup table
        self._function_dict = {
            'Loss Event Frequency'       : self._gen_betapert_general,
            'Threat Event Frequency'     : self._gen_betapert_general,
            'Contact'                    : self._gen_betapert_zero_to_one,
            'Action'                     : self._gen_betapert_zero_to_one,
            'Vulnerability'              : self._gen_bernoulli,
            'Control Strength'           : self._gen_betapert_zero_to_one,
            'Threat Capability'          : self._gen_betapert_general,
            'Probable Loss Magnitude'    : self._gen_betapert_general,
            'Primary Loss Factors'       : self._gen_betapert_general,
            'Asset Loss Factors'         : self._gen_betapert_general,
            'Threat Loss Factors'        : self._gen_betapert_general,
            'Secondary Loss Factors'     : self._gen_betapert_general,
            'Organizational Loss Factors': self._gen_betapert_general,
            'External Loss Factors'      : self._gen_betapert_general,
        }
        # Storage of inputs
        self._supplied_values = {'Creation Datetime': str(pd.datetime.now())}

    def get_supplied_values(self):
        '''Fetch params'''
        return self._supplied_values

    def generate(self, target, count, **kwargs):
        '''Function for dispatching request'''
        # Lookup function
        try:
            target_func = self._function_dict[target]
        except KeyError:
            raise FairException(target + ' is not a valid target.')
        # Execute function
        rvs = target_func(target, count, **kwargs)
        self._supplied_values[target] = {**kwargs}
        return rvs

    def _gen_betapert_zero_to_one(self, target, count, **kwargs):
        '''For numbers between 0 and 1'''
        self._check_pert_zero_to_one(target, **kwargs)
        pert = FairBetaPert(**kwargs)
        rvs = pert.random_variates(count)
        return rvs

    def _gen_betapert_general(self, target, count, **kwargs):
        '''Does not technically need to be greater than one.'''
        self._check_pert_general(target, **kwargs)
        pert = FairBetaPert(**kwargs)
        rvs = pert.random_variates(count)
        return rvs

    def _gen_bernoulli(self, target, count, **kwargs):
        self._check_bernoulli(target, **kwargs)
        bernoulli = scipy.stats.bernoulli(**kwargs)
        rvs = bernoulli.rvs(count)
        return rvs

    def _check_pert_general(self, target, **kwargs):
        conditions_met = [
            kwargs['low']  >= 0              and 
            kwargs['mode'] >  kwargs['low']  and
            kwargs['high'] >  kwargs['mode'] and
            'low' in kwargs.keys()           and
            'mode' in kwargs.keys()          and
            'high' in kwargs.keys()
        ]
        # If all conditions are not met
        if not all(conditions_met):
            raise FairException(str(kwargs) + ' does not meet requirements for general PERT.')

    def _check_pert_zero_to_one(self, target, **kwargs):
        conditions_met = [
            kwargs['low']  >= 0              and
            kwargs['mode'] >  kwargs['low']  and
            kwargs['high'] >  kwargs['mode'] and
            kwargs['high'] <= 1              and
            'low' in kwargs.keys()           and
            'mode' in kwargs.keys()          and
            'high' in kwargs.keys()
        ]
        # If all conditions are not met
        if not all(conditions_met):
            raise FairException(str(kwargs) + ' does not meet requirements for PERT between 0 and 1.')

    def _check_bernoulli(self, target, **kwargs):
        conditions_met = [
            kwargs['p'] >= 0 and
            kwargs['p'] <= 1 and
            'p' in kwargs.keys()
        ]
        # If all conditions are not met
        if not all(conditions_met):
            raise FairException(str(kwargs) + ' does not meet the requirements for Bernoulli distribution.')


class FairCalculations(object):
    '''A class to perform calculations'''
    
    def __init__(self):
        self._data = None
        # Lookup table (no leaf nodes required)
        self._function_dict = {
            'Risk'                       : self._calculate_addition,
            'Loss Event Frequency'       : self._calculate_multiplication,
            'Threat Event Frequency'     : self._calculate_multiplication,
            'Vulnerability'              : self._calculate_step,
            'Probable Loss Magnitude'    : self._calculate_addition,
            'Primary Loss Factors'       : self._calculate_multiplication,
            'Threat Loss Factors'        : self._calculate_multiplication,
            'Secondary Loss Factors'     : self._calculate_multiplication,
        }

    def calculate(self, parent_name, child_1_data, child_2_data):
        '''General function for dispatching calculations'''
        target_function = self._function_dict[parent_name]
        calculated_result = target_function(parent_name, child_1_data, child_2_data)
        return calculated_result
    
    def _calculate_step(self, parent_name, child_1_data, child_2_data):
        '''Create a bool series, which can be multiplied as 0/1 value'''
        return child_1_data > child_2_data
    
    def _calculate_addition(self, parent_name, child_1_data, child_2_data):
        '''Calculate sum of two columns'''
        return child_1_data + child_2_data
    
    def _calculate_multiplication(self, parent_name, child_1_data, child_2_data):
        '''Calculate product of two columns'''
        return child_1_data * child_2_data


class FairMetaModel(object):
    '''A collection of models.'''

    def __init__(self, name=None, models=None, metamodel_uuid=None):
        self._name = name
        self._params = {}
        self._risk_table = pd.DataFrame()
        # For every model, flatten and save params.
        for model in models:
            self._record_params(model)
            self._calculate_model(model)
        # UUID
        if metamodel_uuid:
            self._metamodel_uuid = metamodel_uuid
        else:
            self._metamodel_uuid = str(uuid.uuid1())

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
        data['metamodel_uuid'] = self._metamodel_uuid
        data['type'] = str(self.__class__)
        json_data = json.dumps(
            data,
            indent=4,
        )
        return json_data
