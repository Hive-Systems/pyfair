import scipy.stats

import numpy as np
import pandas as pd

from ..utility.fair_exception import FairException
from ..utility.beta_pert import FairBetaPert


class FairDataInput(object):
    '''Data entry and validation.'''
    
    # TODO confirm accuracy of these function mappings.
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
        # If constant test and fill
        if 'constant' in kwargs.keys():
            self._check_constant(target, **kwargs)
            self._supplied_values[target] = {**kwargs}
            return np.full(count, kwargs['constant'])
        # If not contstant, get target funciton and run
        else:
            rvs = target_func(target, count, **kwargs)
            self._supplied_values[target] = {**kwargs}
            return rvs

    def _gen_betapert_zero_to_one(self, target, count, **kwargs):
        '''For numbers between 0 and 1'''
        self._check_pert_general(target, **kwargs)
        if kwargs['high'] > 1:
            err = 'Params {} fail PERT between zero and one requirement'.format(kwargs)
            raise FairException(err)
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
        conditions = {
            'low >= 0'     : kwargs['low']  >= 0,
            'mode >= low'  : kwargs['mode'] >= kwargs['low'],
            'high >= mode' : kwargs['high'] >= kwargs['mode'],
            'low supplied' : 'low'  in kwargs.keys(),
            'mode supplied': 'mode' in kwargs.keys(),
            'high supplied': 'high' in kwargs.keys(),
        }
        for condition_name, condition_value in conditions.items():
            if condition_value == False:
                err = 'Params {} fail PERT requirement "{}".'.format(kwargs, condition_name)
                raise FairException(err)

    def _check_bernoulli(self, target, **kwargs):
        conditions_met = [
            kwargs['p'] >= 0 and
            kwargs['p'] <= 1 and
            'p' in kwargs.keys()
        ]
        # If all conditions are not met
        if not all(conditions_met):
            raise FairException(str(kwargs) + ' does not meet the requirements for Bernoulli distribution.')

    def _check_constant(self, target, **kwargs):
        '''Check if constant is below zero (or equal to or less one in some circumstnaces)'''
        if kwargs['constant'] < 0:
            raise FairException(str(kwargs) + ' has a number less than zero.')
        associated_func = self._function_dict[target]
        zero_to_one_functs = [
            self._gen_betapert_zero_to_one, 
            self._gen_bernoulli
        ]
        if associated_func in zero_to_one_functs:
            if kwargs['constant'] > 1:
                raise FairException(str(kwargs) + ' has a constant number greater than is allowed.')
