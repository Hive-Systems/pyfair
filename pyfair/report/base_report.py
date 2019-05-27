import base64
import inspect
import io
import os
import pathlib

import pandas as pd

from .. import VERSION

from .tree_graph import FairTreeGraph
from .distribution import FairDistributionCurve
from .exceedence import FairExceedenceCurves
from ..utility.fair_exception import FairException
from .violin import FairViolinPlot


class FairBaseReport(object):
    '''A base report class with boilerplate.'''

    def __init__(self):
        # Add formatting strings
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
        frame = inspect.getouterframes(inspect.currentframe())[2]
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
