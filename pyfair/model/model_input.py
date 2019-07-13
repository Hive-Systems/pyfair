import scipy.stats

import numpy as np
import pandas as pd

from ..utility.fair_exception import FairException
from ..utility.beta_pert import FairBetaPert


class FairDataInput(object):
    '''Data entry and validation.
    
    TODO: confirm accuracy of these function mappings.
    
    '''
    
    def __init__(self):
        # These targets must be less than or equal to one
        self._le_1_targets = ['Action', 'Vulnerability', 'Control Strength', 'Threat Capability']
        self._le_1_keywords = ['constant', 'high', 'mode', 'low', 'mean', 'p']
        # Parameter map associates parameters with functions
        self._parameter_map = {
            'constant': self._gen_constant,
            'high'    : self._gen_pert,
            'mode'    : self._gen_pert,
            'low'     : self._gen_pert,
            'gamma'   : self._gen_pert,
            'mean'    : self._gen_normal,
            'stdev'   : self._gen_normal,
            'p'       : self._gen_bernoulli,
        }
        # Vulnerability is bernoulli only.
        self._bernoulli_targets = ['Vulnerability']
        # List of keywords with function keys
        self._required_keywords = {
            self._gen_constant : ['constant'],
            self._gen_pert     : ['low', 'mode', 'high'],
            self._gen_normal   : ['mean', 'stdev'],
            self._gen_bernoulli: ['p']
        }  
        # Storage of inputs
        self._supplied_values = {}

    def get_supplied_values(self):
        '''Fetch params'''
        return self._supplied_values
    
    def _check_le_1(self, target, **kwargs):
        '''Checks if certain keyword arguments are less than 1'''
        # For every keyword argument
        for key, value in kwargs.items():
            # If key is in specified list
            if key in self._le_1_keywords:
                # Check if value is less than or equal to 1
                if 0.0 <= value <= 1.0:
                    pass
                # If not, raise error
                else:
                    raise FairException('"{}" must have "{}" value between zero and one.'.format(target, key))

    def _check_parameters(self, target_function, **kwargs):
        '''Look up keywords based on function type'''
        required_keywords = self._required_keywords[target_function]
        for required_keyword in required_keywords:
            if required_keyword in kwargs.keys():
                pass
            else:
                raise FairException('"{}" is missing "{}".'.format(str(target_function), required_keyword))

    def generate(self, target, count, **kwargs):
        '''Function for dispatching a generation request'''
        # Generate result
        result = self._generate_single(target, count, **kwargs)
        # Explicitly insert optional keywords for model storage
        dict_keys = kwargs.keys()
        if 'low' in dict_keys and 'gamma' not in dict_keys:
            kwargs['gamma'] = 4
        # Record and return
        self._supplied_values[target] = {**kwargs}
        return result
    
    def _generate_single(self, target, count, **kwargs):
        '''Internal function for single request'''
        # If destined for a le_1_target, check validity.
        if target in self._le_1_targets:
            self._check_le_1(target, **kwargs)
        # If target is bernoulli, shunt into that function.
        if target in self._bernoulli_targets:
            results = self._gen_bernoulli(count, **kwargs)
        else:
            # Otherwise figure out what function
            func = self._determine_func(**kwargs)
            # Check to make sure sufficient parameters exist
            self._check_parameters(func, **kwargs)
            # Run the function
            results = func(count, **kwargs)
        return results

    def generate_multi(self, prefixed_target, count, kwargs_dict):
        # Remove prefix from target
        final_target = prefixed_target.lstrip('multi_')
        # Create a container for dataframes
        df_dict = {target: pd.DataFrame() for target in kwargs_dict.keys()}
        # For each target
        for target, column_dict in kwargs_dict.items():
            # For each column in that garget
            for column, params in column_dict.items():
                # Gen data
                data = self._generate_single(target, count, **params)
                s = pd.Series(data)
                # Put in dict
                df_dict[target][column] = s
        # Multiply
        df1, df2 = df_dict.values()
        combined_df = df1 * df2
        # Sum
        summed = combined_df.sum(axis=1)
        # Record params
        new_target = 'multi_' + final_target
        self._supplied_values[new_target] = kwargs_dict
        return summed
            
    def _determine_func(self, **kwargs):
        '''This function takes keywords and determines function'''
        # Check whether keys are recognized
        for key in kwargs.keys():
            if not key in self._parameter_map.keys():
                raise FairException('"{}"" is not a recognized keyword'.format(key))
        # Check whether all keys go to same function via set comprension
        functions = list(set([
            self._parameter_map[key]
            for key
            in kwargs.keys()
        ]))
        if len(functions) > 1:
            raise FairException('"{}" mixes incompatible keywords.'.format(str(kwargs.keys())))
        else:
            function = functions[0]
            return function

    def _gen_bernoulli(self, count, **kwargs):
        # No check required as 0 to 1 is already esablished
        bernoulli = scipy.stats.bernoulli(**kwargs)
        rvs = bernoulli.rvs(count)
        return rvs
    
    def _gen_constant(self, count, **kwargs):
        return np.full(count, kwargs['constant'])
    
    def _gen_normal(self, count, **kwargs):
        normal = scipy.stats.norm(loc=kwargs['mean'], scale=kwargs['stdev'])
        rvs = normal.rvs(count)
        # Clip out of range values
        clipped_rvs = np.clip(rvs, 0.0, 1.0)
        return clipped_rvs
    
    def _gen_pert(self, count, **kwargs):
        self._check_pert(**kwargs)
        pert = FairBetaPert(**kwargs)
        rvs = pert.random_variates(count)
        return rvs
    
    def _check_pert(self, **kwargs):
        conditions = {
            'mode >= low'  : kwargs['mode'] >= kwargs['low'],
            'high >= mode' : kwargs['high'] >= kwargs['mode'],
        }
        for condition_name, condition_value in conditions.items():
            if condition_value == False:
                err = 'Param "{}" fails PERT requirement "{}".'.format(kwargs, condition_name)
                raise FairException(err)
