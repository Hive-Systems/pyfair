import scipy.stats

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
