"""Distribution curve for histogram and PDF creation"""

import warnings

import numpy as np
import matplotlib.pyplot as plt

from matplotlib.ticker import StrMethodFormatter
from scipy.stats import beta

from ..report.base_curve import FairBaseCurve


class FairDistributionCurve(FairBaseCurve):
    """A shiny distribution curve to lend credibility to guesstimates.

    This object is used to generate two separarate distributions: 1) a main
    distribution curve with pdf to analyze Risk distribution, and 2) a
    miniature distribution which covers the spread of an individual
    input argument.

    Parameters
    ----------
    model_or_iterable : FairModel, FairMetaModel, or list of 
    FairModels/FairMetaModels

    Examples
    --------
    >>> m = pyfair.model.FairModel.from_json('model_1.json')
    >>> dc = pyfair.report.FairDistributionCurve(m) 

    """
    def __init__(self, model_or_iterable, currency_prefix='$'):
        self._input = self._input_check(model_or_iterable)
        self._currency_prefix = currency_prefix

    def generate_icon(self, model_name, target):
        """Generate a minimalist histogram for for a given model/parameter

        Parameters
        ----------
        model_name : str
            The name of the model for which to generate the histogram

        target : str
            The name of the parameter for which to generate the histogram

        Returns
        -------
        (matplotlib.figure, matplotlib.ax)
            A tuple containing the figure and axis generated

        Examples
        --------
        >>> m = pyfair.model.FairModel.from_json('model_1.json')
        >>> dc = pyfair.report.FairDistributionCurve(m)
        >>> fig, ax = dc.generate_icon()

        """
        model = self._input[model_name]
        data = model.export_results().loc[:, target]
        # Set up ax and params
        fig, ax = plt.subplots(figsize=(25, 1))
        ax.set_xlim(0, data.max())
        # Set spines and axis invisible
        for spine in ['left', 'right', 'top', 'bottom']:
            ax.spines[spine].set_visible(False)
        plt.tick_params(bottom=False)
        ax.yaxis.set_visible(False)
        # Tweak ticks based on content
        if data.max() <= 1:
            ax.axes.xaxis.set_major_formatter(StrMethodFormatter('{x:,.2f}'))
            plt.xticks([0, 1])
        else:
            ax.axes.xaxis.set_major_formatter(StrMethodFormatter('{x:,.0f}'))
            plt.xticks([0, data.max()])
        # Plot data (range is required)
        plt.hist(data, bins=100, range=(0, data.max()), alpha=.4)
        plt.vlines(data.mean(), 0, plt.ylim()[1], linestyle='--')
        plt.tight_layout()
        return (fig, ax)

    def generate_image(self):
        """Provides histogram(s) with PDF curve(s)

        Returns
        -------
        (matplotlib.figure, matplotlib.ax)
            A tuple containing the figure and axis generated

        Examples
        --------
        >>> m = pyfair.model.FairModel.from_json('model_1.json')
        >>> dc = pyfair.report.FairDistributionCurve(m)
        >>> fig, ax = dc.generate_image()

        """
        # Setup plots
        
        fig, ax = plt.subplots(figsize=(16, 6))
        plt.subplots_adjust(bottom=.2)
        ax.axes.set_title('Risk Distribution', fontsize=20)
        ax.locator_params(axis='x', nbins=25)
        # Format X axis
        ax.axes.xaxis.set_major_formatter(StrMethodFormatter(self._currency_prefix + '{x:,.0f}'))
        ax.axes.xaxis.set_tick_params(rotation=-45)
        ax.axes.grid(color='b', linestyle='-', linewidth=1, alpha=.1)
        ax.set_ylabel('Frequency Histogram')
        ax.axes.xaxis.set_tick_params(left = 'true')
        #for tick in ax.axes.xaxis.get_major_ticks():
            #tick.label.set_horizontalalignment('left')
        # Draw histrogram for each model
        legend_labels = []
        for name, model in self._input.items():
            legend_labels.append(name)
            plt.hist(
                [model.export_results()['Risk']], 
                bins=25,
                alpha=.3
            )
        ax.legend(legend_labels, frameon=False)
        # Min and Max post graphing
        xmin, xmax = ax.get_xlim()
        # Now draw twin axis a d style
        tyax = plt.twinx(ax)
        tyax.set_ylabel('PDF')
        tyax.set_yticks([])
        # Plot for each
        for name, model in self._input.items():
            risk = model.export_results()['Risk']
            # Catch warnings as we're "fitting" with known shape parameters.
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                beta_curve = beta(*beta.fit(risk))
            space = np.linspace(0, xmax, 1000)
            tyax.plot(space, beta_curve.pdf(space))
        plt.margins(0)
        return (fig, ax)
