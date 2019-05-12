import scipy.stats
import numpy as np
import pandas as pd


class FairException(Exception):
    '''Vanity exception class'''
    pass


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
        # And placeholders for reference
        self._mean  = None
        self._stdev = None
        self._alpha = None
        self._beta  = None
        # And a data table for vectorized calculations
        self._generation_table  = pd.DataFrame()
        # Run mean, alpha, and beta calcs in sequence. Generate curve.
        self._generate_mean()
        self._generate_stdev()
        self._generate_alpha()
        self._generate_beta()
        self._beta_curve = scipy.stats.beta(
            self._alpha, 
            self._beta, 
            self._low,
            self._range,
        )
        
    def _generate_mean(self):
        self._mean = (
            (self._low + self._gamma * self._mode + self._high)
            /
            (self._gamma + 2)
        )
    
    def _generate_stdev(self):
        self._stdev = (
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
        self._alpha = group_1 * (group_2 - 1)

    def _generate_beta(self):
        beta_numerator   = self._alpha * (self._high - self._mean)
        beta_denominator = self._mean - self._low
        self._beta       = beta_numerator / beta_denominator
    
    def random_variates(self, count):
        '''Get n PERT-distributed random numbers'''
        # Alias for previty
        gt = self._generation_table
        # Create uniformly distributed random numbers
        gt['uniform'] = np.random.rand(count)
        # Convert using probability point function (percentile)
        gt['sample'] = self._beta_curve.ppf(gt['uniform'])
        return gt['sample']


class FairDatabase(object):
    '''An interface for a database that stores FAIR results, reports, and metadata.'''
    
    def __init__(self, path_to_database):
        raise NotImplementedError()