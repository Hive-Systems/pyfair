import numpy as np
import matplotlib.pyplot as plt

from matplotlib.ticker import StrMethodFormatter
from scipy.stats import beta

from pyfair.report.base_curve import FairBaseCurve


class FairDistributionCurve(FairBaseCurve):
    '''A shiny distribution curve to lend credibility to our guesstimates.'''
    
    def __init__(self, model_or_iterable):
        self._input = self._input_check(model_or_iterable)
        
    def generate_icon(self, model_name, target):
        '''Minimalist histogram (not for comparisons)'''
        model = self._input[model_name]
        data = model.export_results().loc[:, target]
        # Set up ax and params
        fig, ax = plt.subplots(figsize=(4, .5))
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
        return (fig, ax)
    
    def generate_image(self):
        '''Provides histogram(s) with PDF curve(s)'''
        # Setup plots
        fig, ax = plt.subplots(figsize=(8, 3))
        ax.axes.set_title('Risk Distribution', fontsize=20)
        # Format X axis
        ax.axes.xaxis.set_major_formatter(StrMethodFormatter('${x:,.0f}'))
        ax.axes.xaxis.set_tick_params(rotation=-45)
        ax.set_ylabel('Frequency Histogram')
        for tick in ax.axes.xaxis.get_major_ticks():
            tick.label.set_horizontalalignment('left')
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
            beta_curve = beta(*beta.fit(risk))
            space = np.linspace(0, xmax, 1000)
            tyax.plot(space, beta_curve.pdf(space))
        plt.margins(0)
        return (fig, ax)
