'''An abstract class from which FairModel and FairMetaModel are derived'''

import abc

import numpy as np
import pandas as pd

import scipy.stats as stats

from ..utility.fair_exception import FairException


class FairBase(abc.ABC):

    def __init__(self):
        self._name = NotImplemented
        self._model_uuid = NotImplemented

    ##########################################################################
    # Inspection methods
    ##########################################################################

    def get_name(self):
        """Returns the model name.

        Returns
        -------
        str
            The name of the model.

        """
        return self._name

    def get_uuid(self):
        """Returns the model's unique ID.

        Returns
        -------
        str
            The UUID of the model.

        """
        return self._model_uuid

    @abc.abstractmethod
    def calculation_completed(self):
        raise NotImplementedError()

    ##########################################################################
    # Creation Methods methods
    ##########################################################################

    @abc.abstractstaticmethod
    def read_json(json_data):
        raise NotImplementedError()

    ##########################################################################
    # Calculation methods
    ##########################################################################

    @abc.abstractmethod
    def calculate_all(self):
        raise NotImplementedError()

    ##########################################################################
    # Export methods
    ##########################################################################

    @abc.abstractmethod
    def export_params(self):
        raise NotImplementedError()

    @abc.abstractmethod
    def export_results(self):
        raise NotImplementedError()

    @abc.abstractmethod
    def to_json(self):
        raise NotImplementedError()

    def get_exceedence_probability(self):
        """Get the percentle score for each risk value
        
                Returns
                -------
                pd.Series
                    An index containing a range of all percentages and 
                    values of associated Risks (i.e. for a given
                    percentage, what proportion of final Risks will fall
                    above that percentile).
                
                Raises
                ------
                FairException
                    If model has not been calculated, error raised.

        """
        if self.calculation_completed():
            risk = self.export_results()['Risk']
            value_space = pd.Series(np.linspace(0, risk.max(), 100))
            quantiles = value_space.map(lambda x: stats.percentileofscore(risk, x))
            return pd.Series(index=value_space.values, data=quantiles.values)
        else:
            raise FairException("Model has not yet been calculated.")

    def get_loss_exceedence(self):
        """Get percentage of values under loss value for each value
        
                Returns
                -------
                pd.Series
                    An index containing a range of all Risk values and
                    associated percentages (i.e. for a given loss, what
                    percentage of losses will be below that value).
                
                Raises
                ------
                FairException
                    If model has not been calculated, error raised.

        """
        if self.calculation_completed():
            risk = self.export_results()['Risk']
            value_space = pd.Series(np.linspace(0, risk.max(), 100))
            loss_ex = value_space.map(lambda value: (value < risk).mean())
            loss_ex *= 100
            return pd.Series(index=loss_ex.values, data=value_space.values)
        else:
            raise FairException("Model has not yet been calculated.")
