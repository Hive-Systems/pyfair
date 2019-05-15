import base64
import os
import pathlib

import pandas as pd

from .. import VERSION


class FairBaseReport(object):
    '''A base report class with boilerplate.'''

    def __init__(self, model):
        # Attach model
        self._model = model
        # Add formatting strings
        self._dollar_format_string     = '${0:,}'
        self._integer_format_string    = '{0:,}'
        self._percentage_format_string = '{0:.3f}'
        self._format_strings = {
            'Risk'                        : self._dollar_format_string,
            'Loss Event Frequency'        : self._integer_format_string,
            'Threat Event Frequency'      : self._integer_format_string,
            'Vulnerability'               : self._integer_format_string,         
            'Contact'                     : self._percentage_format_string,
            'Action'                      : self._percentage_format_string,
            'Threat Capability'           : self._percentage_format_string,
            'Control Strength'            : self._percentage_format_string,
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
        self._template_paths = {
            'css'       : self._static_location / 'fair.css',
            'individual': self._static_location / 'individual.html'
        }

    def base64ify(self, image_path, alternative_text='', options=''):
        '''Loads an image into a base64 embeddable <img> tag'''
        # Read data.
        with open(image_path, 'rb') as f:
            binary_data = f.read()
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
    
    def _get_metadata_table(self):
            # Add metadata
        metadata = pd.Series({
            'Author': os.environ['USERNAME'],
            'Created': str(pd.datetime.now()).partition('.')[0],
            'PyFair Version': VERSION,
            'Type': type(self).__name__
        }).to_frame().to_html(border=0, header=None, justify='left', classes='fair_metadata_table')
        return metadata
