"""Violin plot for plotting metamodel risk"""

import matplotlib
import matplotlib.pyplot as plt

from ..utility.fair_exception import FairException
from .base_curve import FairBaseCurve


class FairViolinPlot(FairBaseCurve):
    """Provides a violin-style area plot to summarize MetaModels.

    Parameters
    ----------
    metamodel : FairMetaModel
        The metamodel being analyzed

    """
    def __init__(self, metamodel):
        # If it's just a model, make it a list.
        super().__init__()
        if not metamodel.__class__.__name__ == 'FairMetaModel':
            raise FairException('This requires a metamodel')
        self._metamodel = metamodel

    def generate_image(self):
        """Main function for generating plots

        Returns
        -------
        tuple(matplotlib.figure, matplotlib.axis)
            The figure and axis associated with the FairTreeGraph

        """
        # Setup plots
        fig, ax = plt.subplots(figsize=(16, 8))
        # For each model, calculate and plot.
        columns = self._metamodel.export_results().columns
        ax.violinplot(
            self._metamodel.export_results().values,
            showmeans=False,
            showmedians=True
        )
        ax.axes.xaxis.set_ticks([item for item in range(1, len(columns) + 1)])
        ax.axes.xaxis.set_ticklabels(columns)
        ax.set_title('Components And Aggregate Risk', fontsize=20)
        ax.axes.yaxis.set_major_formatter(matplotlib.ticker.StrMethodFormatter('${x:,.0f}'))
        plt.subplots_adjust(left=.2)
        return (fig, ax)
