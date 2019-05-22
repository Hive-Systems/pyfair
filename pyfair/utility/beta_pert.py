import scipy.stats
import numpy as np
import pandas as pd

from .fair_exception import FairException


class FairBetaPert(object):
    '''A PERT distribution for all your pseudoscientific needs.
    
    Formula taken from:
        https://www.rdocumentation.org/packages/prevalence/versions/0.4.0/topics/betaPERT
        http://mech.vub.ac.be/teaching/info/Ontwerpmethodologie/Appendix%20les%202%20PERT.pdf
        
    '''
    
    def __init__(self, low, mode, high, gamma=4):
        # Populate object with inputs
        self._low   = low
        self._mode  = mode
        self._high  = high
        self._gamma = gamma
        self._range = high - low
        # Run sanity check
        self._run_range_check()
        # Run mean, alpha, and beta calcs in sequence.
        self._mean  = self._generate_mean()
        self._stdev = self._generate_stdev()
        self._alpha = self._generate_alpha()
        self._beta  = self._generate_beta()
        # Generate curve
        self._beta_curve = scipy.stats.beta(
            self._alpha, 
            self._beta, 
            self._low,
            self._range,
        )
    
    def _run_range_check(self):
        if self._range == 0:
            raise FairException('"low" value must be less than "high" value.')

    def _generate_mean(self):
        return (
            (self._low + self._gamma * self._mode + self._high)
            /
            (self._gamma + 2)
        )
    
    def _generate_stdev(self):
        return (
            (self._high - self._low)
            /
            (self._gamma + 2)
        )
    
    def _generate_alpha(self):
        group_1 = (self._mean - self._low) / (self._high - self._low)
        group_2 = ((self._mean - self._low) * (self._high - self._mean) 
                  / 
                  (self._stdev ** 2)
        )
        return group_1 * (group_2 - 1)

    def _generate_beta(self):
        beta_numerator   = self._alpha * (self._high - self._mean)
        beta_denominator = self._mean - self._low
        return beta_numerator / beta_denominator
    
    def random_variates(self, count):
        '''Get n PERT-distributed random numbers'''
        return self._beta_curve.rvs(count)
