"""Module for generating a tree graph"""

import pandas as pd

import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from matplotlib.patches import Rectangle
from matplotlib.collections import PatchCollection


class FairTreeGraph(object):
    """Provides a pretty tree diagram to summarize calculations.

    This tree class provides an image that descirbes those nodes that have
    been calculated, those nodes that have had data supplied, and those
    nodes which are not required.

    Parameters
    ----------
    model : FairModel
        The model which is being described by the tree
    format_strings : dict of str
        A dict with string keys describing the nodes, and string values
        providing a formatting string for numbers of that type

    """
    # Class attribute with magic numbers galore
    _DIMENSIONS = pd.DataFrame.from_dict(
        {
            'Contact Frequency'             : ['C'   ,    0,    0,  600,  800],
            'Threat Event Frequency'        : ['TEF' ,  600,  800, 1800, 1600],
            'Probability of Action'         : ['A'   , 1200,    0,  600,  800],
            'Threat Capability'             : ['TC'  , 2400,    0, 3000,  800],
            'Vulnerability'                 : ['V'   , 3000,  800, 1800, 1600],
            'Control Strength'              : ['CS'  , 3600,    0, 3000,  800],
            'Loss Magnitude'                : ['LM'  , 6600, 1600, 4200, 2400],
            'Loss Event Frequency'          : ['LEF' , 1800, 1600, 4200, 2400],
            'Risk'                          : ['R'   , 4200, 2400, 4200, 5000],
            'Primary Loss'                  : ['PL'  , 5400,  800, 6600, 1600],
            'Secondary Loss'                : ['SL'  , 7800,  800, 6600, 1600],
            'Secondary Loss Event Frequency': ['SLEF', 7200,    0, 7800,  800],
            'Secondary Loss Event Magnitude': ['SLEM', 8400,    0, 7800,  800],
        }, 
        orient='index', 
        columns=['tag', 'self_x', 'self_y', 'parent_x', 'parent_y']
    )

    def __init__(self, model, format_strings):
        self._colormap = {'Not Required': 'grey', 'Supplied': 'green', 'Calculated': 'blue'}
        self._results = model.export_results().T
        self._format_strings = format_strings
        # Calculate mean and standard deviation for results
        self._result_summary = pd.DataFrame({
            'μ': self._results.mean(axis=1), 
            'σ': self._results.std(axis=1),
            '↑': self._results.max(axis=1),
        })
        # Make status input into a dataframe.
        self._statuses = model.get_node_statuses()
        self._process_statuses()
        # Make params a frame (must occur after process_statuses())
        self._params = pd.DataFrame(model.export_params()).T.reindex(self._statuses.index)
        # Tack all data together
        self._data = pd.concat([
            self._statuses,
            self._DIMENSIONS,
            self._result_summary,
            self._params
        ], axis=1, sort=True)
        # Add format strinsg (forgot to add previously)
        self._data['formatter'] = pd.Series(self._format_strings)

    def _process_statuses(self):
        """Turn dict into df and add color column"""
        self._statuses = pd.DataFrame.from_records([self._statuses]).T
        self._statuses.columns = ['status']
        self._statuses['color'] = self._statuses['status'].map(self._colormap)

    def _tweak_axes(self, ax):
        """Add title and run common changes"""
        # Set limits
        ax.set_title('Calculation Dependency Tree', fontsize=20)
        ax.set_xlim(0, 9_400)
        ax.set_ylim(0, 2_900)
        # Disappear axes and spines
        for axis in [ax.xaxis, ax.yaxis]:
            axis.set_visible(False)
        for spine_name in ['left', 'right', 'top', 'bottom']:
            ax.spines[spine_name].set_visible(False)
        return ax

    def _generate_rects(self, ax):
        """Generate rectangles, which cannot be done via apply"""
        patches = []
        patch_colors = []
        for index, row in self._data.iterrows():
            rect = Rectangle(
                (row['self_x'], row['self_y']),
                1000,
                500,
                alpha=.3,
            )
            patches.append(rect)
            patch_colors.append(row['color'])
        collection = PatchCollection(patches, facecolor=patch_colors, alpha=.3)
        ax.add_collection(collection)
        return ax

    def _generate_text(self, row, ax):
        """Apply-able function to gnereate text in rectangles"""
        # Draw header
        plt.text(
            row['self_x'] + 500, 
            row['self_y'] + 370, 
            row['tag'], 
            horizontalalignment='center',
            fontsize=14,
            fontweight='bold',
        )
        # Draw data
        fmt = row['formatter']
        # Set conditions
        calculated = row['status'] == 'Calculated'
        supplied = row['status'] == 'Supplied'
        # Raw inputs will have a list
        if 'raw' in row.index:
            if isinstance(row['raw'], list):
                raw = True
            else:
                raw = False
        else:
            raw = False
        if calculated:
            # Get rid of items with value
            data = row.loc[['μ', 'σ', '↑']].dropna()
            # Get max legnth for justification
            data = data.map(lambda x: fmt.format(x))
            value_just = data.str.len().max()
            # Create output
            output = '\n'.join([
                key + '  ' + value.rjust(value_just)
                for key, value
                in data.items()
            ])
        elif supplied:
            # Get rid of value less items and rename
            data = row.reindex(['high', 'mode', 'low', 'mean', 'stdev'])
            data.index = ['↑', '-', '↓', 'μ', 'σ']
            data = data.dropna()
            # Format string
            data = data.map(lambda x: fmt.format(x))
            # Get max length of stirng
            value_just = data.str.len().max()
            # Output format for raw
            if raw:
                output = '\n'.join([
                    key + '  ' + value.rjust(value_just)
                    for key, value
                    in data.items()
                ])
                output = 'Raw input'
            # And verything else ... so much nesting
            else:
                output = '\n'.join([
                    key + '  ' + value.rjust(value_just)
                    for key, value
                    in data.items()
                ])
        else:
            output = ''
        plt.text(
            row['self_x'] + 25, 
            row['self_y'] + 50, 
            output,
            horizontalalignment='left',
            fontsize=8,
            fontfamily='monospace'
        )

    def _generate_lines(self, row, ax):
        """Generate lines between boxes"""
        if (row['color'] != 'grey') and row.name != 'Risk':
            ax.annotate(
                None,
                xy=(row['parent_x'] + 500, row['parent_y']), 
                xytext=(row['self_x'] + 500, row['self_y'] + 500),     
                arrowprops=dict(
                    arrowstyle="-",
                    connectionstyle="angle3,angleA=0,angleB=-90",
                    ec=row['color'],
                    alpha=.3,
                    linestyle='--', 
                    linewidth=3
                ),
            )

    def _generate_legend(self, ax):
        """Simply function to generate legend"""
        # Gen legend
        patches = [Patch(color=color, label=label, alpha=.3) for label, color in self._colormap.items()]
        plt.legend(handles=patches, frameon=False)

    def generate_image(self):
        """Function to orchestate image and axis generation for the tree

        Specifically, this creates the axes, tweaks them as necessary,
        creates node text, creates rectangles for the nodes, generates the
        lines, and then generates the legend. It takes no arguments as it
        obtains the majority of this information from data passed to the
        FairTreeGraph object.

        Returns
        -------
        tuple(matplotlib.figure, matplotlib.axis)
            The figure and axis associated with the FairTreeGraph

        """
        fig, ax = plt.subplots()
        fig.set_size_inches(20, 6)
        ax = self._tweak_axes(ax)
        self._data.apply(self._generate_text, args=[ax], axis=1)
        self._generate_rects(ax)
        self._data.apply(self._generate_lines, args=[ax], axis=1)
        self._generate_legend(ax)
        return (fig, ax)