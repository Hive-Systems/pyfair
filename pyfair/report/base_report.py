import base64
import io
import os
import pathlib

import pandas as pd

from .. import VERSION

from .tree_graph import FairTreeGraph


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
    
    def _get_metadata_table(self):
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
        data = io.BytesIO()
        fig.savefig(data, format='png')
        # Seek to start of file
        data.seek(0)
        img_tag = self.base64ify(data.read())
        return img_tag
