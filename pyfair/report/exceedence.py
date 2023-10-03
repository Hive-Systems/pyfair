"""Exceedence curve for viewing threshold values"""

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import scipy.stats as stats

from matplotlib.ticker import StrMethodFormatter

from ..model.model import FairModel
from ..model.meta_model import FairMetaModel
from ..utility.fair_exception import FairException
from ..report.base_curve import FairBaseCurve


class FairExceedenceCurves(FairBaseCurve):
    """Plots one or more exceedence curves"""

    def __init__(self, model_or_iterable, currency_prefix='$'):
        # If it's just a model, make it a list.
        super().__init__()
        self._currency_prefix = currency_prefix
        self._input = self._input_check(model_or_iterable)

    def generate_image(self):
        """Main function for generating plots"""
        # Setup plots
        fig, axes = plt.subplots(1, 2, figsize=(16, 4))
        plt.subplots_adjust(bottom=.3)
        ax1, ax2 = axes
        # For each model, calculate and plot.
        legend_labels = []
        for name, model in self._input.items():
            legend_labels.append(name)
            data = model.export_results()
            # Get Risk Data
            risk = data['Risk']
            risk_max = risk.max()
            # Create feature space
            space = pd.Series(np.linspace(0, risk_max, 100))
            # Get X and Y for each calculation
            prob_xy = self._get_prob_data(space, risk)
            loss_xy = self._get_loss_data(space, risk)
            # Generate curves with x and y
            self._generate_prob_curve(name, ax1, *prob_xy)
            self._generate_loss_curve(name, ax2, *loss_xy)
        ax1.legend(legend_labels, frameon=False)
        ax2.legend(legend_labels, frameon=False)
        return (fig, (ax1, ax2))

    def _get_prob_data(self, space, risk):
        """Get the percentle score for each risk value"""
        quantiles = space.map(lambda x: stats.percentileofscore(risk, x))
        return (quantiles, space)

    def _get_loss_data(self, space, risk):
        """Get percentage of values under loss value for each value"""
        loss_ex = space.map(lambda value: (value < risk).mean())
        return (space, loss_ex * 100)    

    def _generate_prob_curve(self, name, ax, quantiles, space):
        """For each percentile, what is the expected loss?"""
        # Plot
        ax.plot(quantiles, space)
        # Style
        y_formatter = matplotlib.ticker.StrMethodFormatter(self._currency_prefix + '{x:,.0f}')
        ax.axes.yaxis.set_major_formatter(y_formatter)
        x_formatter = matplotlib.ticker.StrMethodFormatter('{x:,.0f}%')
        ax.axes.xaxis.set_major_formatter(x_formatter)
        ax.axes.set_title('Exceedence Probability Curve', fontsize=20)

    def _generate_loss_curve(self, name, ax, space, loss_expectancy):
        """For each dollar amount, what's the probability loss was exceeded?"""
        # Plot
        ax.plot(space, loss_expectancy)
        # Style
        ax.axes.yaxis.set_major_formatter(StrMethodFormatter('{x:,.0f}%'))
        ax.axes.xaxis.set_major_formatter(StrMethodFormatter(self._currency_prefix + '{x:,.0f}'))
        ax.axes.xaxis.set_tick_params(rotation=-45)
        ax.axes.xaxis.set_tick_params(left = 'true')
        #for tick in ax.axes.xaxis.get_major_ticks():
        #    tick.label.set_horizontalalignment('left')
        ax.axes.set_title('Loss Exceedence Curve', fontsize=20)
