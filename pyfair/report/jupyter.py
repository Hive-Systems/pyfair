'''Module for obtaining fig and ax data for use in Jupyter notebook'''

from pyfair import FairModel
from pyfair import FairMetaModel

from pyfair.report.tree_graph import FairTreeGraph
from pyfair.report.distribution import FairDistributionCurve
from pyfair.report.exceedence import FairExceedenceCurves
from pyfair.utility.fair_exception import FairException
from pyfair.report.violin import FairViolinPlot


class FairJupyterShim(object):
    '''Obtains raw figs and axes for use in Jupyter.
    
    Parameters
    ----------
    model_or_models : list of FairModels/FairMetaModels
        The model which is being described by the tree
    format_strings : dict of str
        A dict with string keys describing the nodes, and string values
        providing a formatting string for numbers of that type
    
    Examples
    --------
    >>> shim = FairJupyterShim([model1, model2])
    >>> shim.get_trees()
    {'Basic Model 1': (<Figure size 1440x432 with 1 Axes>, <AxesSubplot:title={'center':'Calculation Dependency Tree'}>),
     'Basic Model 2': (<Figure size 1440x432 with 1 Axes>, <AxesSubplot:title={'center':'Calculation Dependency Tree'}>)}
    
    '''
    def __init__(self,
                 model_or_models,
                 currency_prefix='$'):
        # Add formatting strings
        self._currency_prefix = currency_prefix
        self._model_or_models = self._input_check(model_or_models)
        self._currency_format_string     = currency_prefix + '{0:,.0f}'
        self._float_format_string        = '{0:.2f}'
        self._format_strings = {
            'Risk'                           : self._currency_format_string,
            'Loss Event Frequency'           : self._float_format_string,
            'Threat Event Frequency'         : self._float_format_string,
            'Vulnerability'                  : self._float_format_string,         
            'Contact Frequency'              : self._float_format_string,
            'Probability of Action'          : self._float_format_string,
            'Threat Capability'              : self._float_format_string,
            'Control Strength'               : self._float_format_string,
            'Loss Magnitude'                 : self._currency_format_string,
            'Primary Loss'                   : self._currency_format_string,
            'Secondary Loss'                 : self._currency_format_string,
            'Secondary Loss Event Frequency' : self._float_format_string,
            'Secondary Loss Event Magnitude' : self._currency_format_string,
        }
        
    def _input_check(self, value) -> dict:
        """Check input value for report is appropriate

        Raises
        ------
        FairException
            If an inappropriate object or iterable of objects is supplied

        """
        # If it's a model or metamodel, plug it in a dict.
        rv = {}
        if value.__class__.__name__ in ['FairModel', 'FairMetaModel']:
            rv[value.get_name()] = value
            return rv
        # Check for iterable.
        if not hasattr(value, '__iter__'):
            raise FairException('Input is not a FairModel, FairMetaModel, or an iterable.')
        if len(value) == 0:
            raise FairException('Empty iterable where iterable of models expected.')
        # Iterate and process remainder.
        for proported_model in value:
            # Check if model
            if proported_model.__class__.__name__ in ['FairModel', 'FairMetaModel']:
                # Check if calculated
                if proported_model.calculation_completed():
                    rv[proported_model.get_name()] = proported_model
                else:
                    raise FairException('Model or FairModel has not been calculated.')
            else:
                raise FairException('Iterable member is not a FairModel or FairMetaModel')
        return rv

    def get_trees(self) -> dict:
        """Create a tree image of model iterable
        
        Raises
        ------
        FairException
            When input models include a MetaModel, which is invalid for trees
        
        Returns
        -------
        dict
            A dictionary with the model names as keys and the fig, ax pairs
            as values
        
        """
        rv = {}
        for name, model in self._model_or_models.items():
            if isinstance(model, FairMetaModel):
                raise FairException('Cannot make a tree from metamodel: {}'.format(model))
            else:
                ftg = FairTreeGraph(model, self._format_strings)
                fig_ax = ftg.generate_image()
                rv[name] = fig_ax
        return rv

    def get_distributions(self) -> dict:
        """Create a distribution image of model/metamodels iterable
        
        Returns
        -------
        dict
            A dictionary with the model names as keys and the fig, ax pairs
            of distribution curves as values. The 'combined' keyword denotes
            all of the distributions combined.
        
        """
        # Process individual distributions
        rv = {}
        for name, model in self._model_or_models.items():
            fdc = FairDistributionCurve(model, self._currency_prefix)
            fig, ax = fdc.generate_image()
            rv[name] = (fig, ax)
        # Process combined distributions
        inputs = self._model_or_models.values()
        fdc2 = FairDistributionCurve(inputs, self._currency_prefix)
        fig, ax = fdc2.generate_image()
        rv['combined'] = (fig, ax)
        return rv

    def get_exceedence_curves(self) -> dict:
        """Create a exceedence curves
        
        Returns
        -------
        dict
            A dictionary with the model names as keys and the fig, axes pairs
            of exceedence curves as values. The 'combined' keyword denotes
            all of the distributions combined. Please note that this contains
            1 fig, but 2 axes.
        
        """
        # Process individual curve
        rv = {}
        for name, model in self._model_or_models.items():
            fec = FairExceedenceCurves(model, self._currency_prefix)
            fig, axes = fec.generate_image()
            rv[name] = (fig, axes)
        # Add combined curve
        inputs = self._model_or_models.values()
        fec2 = FairExceedenceCurves(inputs, self._currency_prefix)
        fig, ax = fec2.generate_image()
        rv['combined'] = (fig, ax)
        return rv

    def get_violins(self):
        """Create a exceedence curves
        
        Returns
        -------
        dict
            A dictionary with the metamodel names as the key and the fig, ax
            tuple as the value.
            
        Raises
        ------
        FairException
            If input is a model (violin only addresses metamodels)
        
        """
        rv = {}
        for name, model in self._model_or_models.items():
            if isinstance(model, FairModel):
                raise FairException('Cannot make violin plot from model: {}'.format(model))
        vplot = FairViolinPlot(model)
        fig, ax = vplot.generate_image()
        rv[name] = (fig, ax)
        return rv
