import scipy.stats
import numpy as np
import pandas as pd

from .fair_exception import FairException


class FairBetaPert(object):
    r"""A PERT distribution for all your pseudoscientific needs.

    FAIR often uses PERT or BetaPERT distributions in order to model skewed
    data that must exist between a fixed lower and upper bound. Because a
    BetaPert distribution a specific type of Beta distribution, it is
    possible to precompute the appropriate BetaPert parameters, and then
    simply create a Beta distribution using those parameters.

    Parameters
    ----------
    low : float or int
        Lower bound for the distribution below which no values will fall
    mode : float or int
        The most common value in the distribution
    high : float or int
        Higher bound for the distribution above which no values will fall
    gamma : float or int, optional
        A BetaPERT parameter for narrowing peak, default is 4

    Notes
    -----
    `PERT distributions <https://en.wikipedia.org/wiki/PERT_distribution>`
    are a subset of `Beta distributions
    <https://en.wikipedia.org/wiki/Beta_distribution>` that are often used
    in FAIR analysis for a variety of reasons.

    Where:

    .. math::

        \text{mean}
        =
        \frac
            {\text{low} + \text{gamma} \times \text{mode} + \text{high}}
            {\text{gamma} + 2}

    .. math::

        \text{stdev}
        =
        \frac
            {\text{high} - \text{low}}
            {\text{gamma} + 2}

    .. math::

        \alpha 
        =
        (\text{mean} - \text{low}) 
        \times
        \frac
            {2 \times \text{mode} - \text{low} -\text{high}}
            {(\text{mode} - \text{mean}) \times (\text{high} - \text{low})}

    .. math::

        \beta 
        = 
        \alpha
        \times
        \frac 
            {\text{high} - \text{mean}}
            {\text{mean} - \text{low}}

    References
    ----------
    .. [1] Vose, D. (2000) Risk Analysis: A Quantitative Guide. 2nd
           Edition, John Wiley & Sons, Chichester. 
    
    .. [2] Buchsbaum, Paulo. (2012). Modified Pert Simulation.

    .. [3] Malcolm, D., Roseboom, J., Clark, C., & Fazar, W. (1959).
           Application of a Technique for Research and Development Program
           Evaluation. Operations Research, 7(5), 646-669.

    .. [4] Devleesschauwer, Brecht. (2015). prvalence: Tools for Prevalence
           Assessment Studies. R package version v0.4.0.

    .. note:: Though this class is created in contemplation of using the
              class methods attached, it is possible to obtain the raw
              scipy beta distribution itself via the ._beta_curve
              attribute.

    """
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
