import base64
import inspect
import io
import os
import pathlib

import numpy as np
import pandas as pd

from .. import VERSION

from .tree_graph import FairTreeGraph
from .distribution import FairDistributionCurve
from .exceedence import FairExceedenceCurves
from ..utility.fair_exception import FairException
from .violin import FairViolinPlot


class FairBaseReport(object):
    '''A base report class with boilerplate.
    
    TODO: make an HTML generator. This class is bloated.
    TODO: this should capture errors and warnings in a sep table.
    '''

    def __init__(self):
        # Add formatting strings
        self._model_or_models = None
        self._dollar_format_string     = '${0:,.0f}'
        self._float_format_string      = '{0:.2f}'
        self._format_strings = {
            'Risk'                        : self._dollar_format_string,
            'Loss Event Frequency'        : self._float_format_string,
            'Threat Event Frequency'      : self._float_format_string,
            'Vulnerability'               : self._float_format_string,         
            'Contact'                     : self._float_format_string,
            'Action'                      : self._float_format_string,
            'Threat Capability'           : self._float_format_string,
            'Control Strength'            : self._float_format_string,
            'Probable Loss Magnitude'     : self._dollar_format_string,
            'Primary Loss Factors'        : self._dollar_format_string,
            'Asset Loss Factors'          : self._dollar_format_string,
            'Threat Loss Factors'         : self._dollar_format_string,
            'Secondary Loss Factors'      : self._dollar_format_string,
            'Organizational Loss Factors' : self._dollar_format_string,
            'External Loss Factors'       : self._dollar_format_string,
        }
        # Add locations
        self._fair_location = pathlib.Path(__file__).parent.parent
        self._static_location = self._fair_location / 'static'
        self._logo_location = self._static_location / 'white_python_logo.png'
        self._template_paths = {
            'css'   : self._static_location / 'fair.css',
            'simple': self._static_location / 'simple.html'
        }
        self._caller_source = self._set_caller_source()

    def _set_caller_source(self):
        frame = inspect.getouterframes(inspect.currentframe())[-1]
        filename = frame[1]
        name = pathlib.Path(filename)
        if 'ipython-input' in str(name):
            return 'Report was called from iPython and not a script.'
        elif name.exists():
            return name.read_text()
        else:
            return 'Report was not called from a script file.'

    def _get_caller_source(self):
        return self._caller_source

    def _input_check(self, value):
        # If it's a model or metamodel, plug it in a dict.
        rv = {}
        if value.__class__.__name__ in ['FairModel', 'FairMetaModel']:
            rv[value.get_name()] = value
            return rv
        # Check for iterable.
        if not hasattr(value, '__iter__'):
            raise FairException('Input is not a FairModel, FairMetaModel, or an iterable.')
        # Iterate and process remainder.
        for proported_model in value:
            if proported_model.__class__.__name__ in ['FairModel', 'FairMetaModel']:
                rv[proported_model.get_name()] = proported_model
            else:
                raise FairException('Iterable member is not a FairModel or FairMetaModel')
        return rv

    def get_format_strings(self):
        return self._format_strings

    def base64ify(self, image, alternative_text='', options=''):
        '''Loads an image into a base64 embeddable <img> tag'''
        # If path, open and read.
        if type(image) == str or isinstance(image, pathlib.Path):
            with open(image, 'rb') as f:
                binary_data = f.read()
        # If bytes, jsut write
        elif type(image) == bytes:
            binary_data = image
        else:
            raise TypeError(str(image) + ' is not a string, path, or bytes.')
        # Get base64 string
        base64_string = base64.b64encode(binary_data).decode('utf8')
        # Create tag
        tag = f'<img {options} src="data:image/png;base64, {base64_string}" alt="{alternative_text}"/>'
        return tag

    def _construct_output(self):
        '''Defined by subclass'''
        # Get report
        raise NotImplementedError()

    def to_html(self, output_path):
        output = self._construct_output()
        with open(output_path, 'w+') as f:
            f.write(output)

    def _fig_to_img_tag(self, fig):
        '''Convert fig to base64 encoded img tag'''
        data = io.BytesIO()
        fig.savefig(data, format='png', transparent=True)
        data.seek(0)
        img_tag = self.base64ify(data.read())
        return img_tag

    def _get_data_table(self, model):
        data = model.export_results().dropna(axis=1)
        table = data.to_html(
            border=0, 
            justify='left', 
            classes='fair_metadata_table'
        )
        return table

    def _get_parameter_table(self, model):
        data = model.export_parameters()
        return data       

    def _get_metadata_table(self):
        '''Do not put model-specific data in here.'''
            # Add metadata
        metadata = pd.Series({
            'Author': os.environ['USERNAME'],
            'Created': str(pd.datetime.now()).partition('.')[0],
            'PyFair Version': VERSION,
            'Type': type(self).__name__
        }).to_frame().to_html(border=0, header=None, justify='left', classes='fair_metadata_table')
        return metadata    

    def _get_tree(self, model):
        ftg = FairTreeGraph(model, self._format_strings)
        fig, ax = ftg.generate_image()
        img_tag = self._fig_to_img_tag(fig)
        return img_tag

    def _get_distribution(self, model_or_models):
        fdc = FairDistributionCurve(model_or_models)
        fig, ax = fdc.generate_image()
        img_tag = self._fig_to_img_tag(fig)
        return img_tag

    def _get_distribution_icon(self, model, target):
        fdc = FairDistributionCurve(model)
        fig, ax = fdc.generate_icon(model.get_name(), target)        
        img_tag = self._fig_to_img_tag(fig)
        return img_tag

    def _get_exceedence_curves(self, model_or_models):
        fec = FairExceedenceCurves(model_or_models)
        fig, ax = fec.generate_image()
        img_tag = self._fig_to_img_tag(fig)
        return img_tag
    
    def _get_violins(self, metamodel):
        vplot = FairViolinPlot(metamodel)
        fig, ax = vplot.generate_image()
        img_tag = self._fig_to_img_tag(fig)
        return img_tag
    
    def _get_overview_table(self, model_or_models):
        risk_results = pd.DataFrame({
            name: model.export_results()['Risk']
            for name, model 
            in model_or_models.items()
        })
        risk_results = risk_results.agg([np.mean, np.std, np.min, np.max])
        risk_results.index = ['Mean', 'Stdev', 'Minimum', 'Maximum']
        overview_df = risk_results.applymap(lambda x: self._format_strings['Risk'].format(x))
        overview_df.loc['Simulations'] = [
            '{0:,.0f}'.format(len(model.export_results())) 
            for model 
            in model_or_models.values()
        ]
        overview_df.loc['Identifier'] = [model.get_uuid() for model in model_or_models.values()]
        overview_df.loc['Model Type'] = [model.__class__.__name__ for model in model_or_models.values()]
        overview_html = overview_df.to_html(border=0, header=True, justify='left', classes='fair_table')
        return overview_html

    def _get_model_parameter_table(self, model):
            params = dict(**model.export_params())
            # Remove items we don't want.
            params = {
                key: value 
                for key, value 
                in params.items() 
                if key in self._format_strings.keys()
            }
            fs = self._format_strings
            param_df = pd.DataFrame(params).T
            param_df = param_df[['low', 'mode', 'high']]
            param_df['mean'] = model.export_results().mean(axis=0)
            param_df['stdev'] = model.export_results().std(axis=0)
            param_df['min'] = model.export_results().min(axis=0)
            param_df['max'] = model.export_results().max(axis=0)
            param_df = param_df.apply(
                lambda row: pd.Series(
                    [
                        fs[row.name].format(item) 
                        for item 
                        in row
                    ],
                    index=row.index.values
                ),
                axis=1,
            )
            # Do not truncate our base64 images.
            pd.set_option('display.max_colwidth', -1)
            param_df['distribution'] = [
                self._get_distribution_icon(model, target)
                for target 
                in param_df.index.values
            ]
            detail_table = param_df.to_html(
                border=0, 
                header=True, 
                justify='left', 
                classes='fair_table',
                escape=False
            )
            return detail_table
    
    def _get_metamodel_parameter_table(self, metamodel):
            risk_df = metamodel.export_results().T
            risk_df = pd.DataFrame({
                'mean' : risk_df.mean(axis=1),
                'stdev': risk_df.std(axis=1),
                'min'  : risk_df.min(axis=1),
                'max'  : risk_df.max(axis=1),
            })
            risk_df = risk_df.apply(
                lambda row: pd.Series(
                    [self._format_strings['Risk'].format(item) for item in row],
                    index=row.index.values
                ),
                axis=1,
            )
            # Do not truncate our base64 images.
            detail_table = risk_df.to_html(
                border=0, 
                header=True, 
                justify='left', 
                classes='fair_table',
                escape=False
            )
            return detail_table
        
