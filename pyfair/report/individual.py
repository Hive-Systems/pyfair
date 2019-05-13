import os

import pandas as pd

from .base import FairBaseReport
from .. import VERSION


class FairReport(FairBaseReport):
    
    def __init__(self, model):
        super().__init__(model)

    def _construct_output(self):

        # Get report
        report = self._template_paths['individual'].read_text()

        # Add CSS via STyle tag
        css = self._template_paths['css'].read_text()
        report = report.replace('{STYLE}', css)

        # Add Python image
        python_image = self._static_location / 'white_python_logo.PNG'
        python_img_tag = self.base64ify(python_image, options='width="80px" style="padding: 20px 20px 20px 20px"')
        report = report.replace('{PYTHON_LOGO}', python_img_tag)

        # Add metadata
        metadata = pd.Series({
            'Author': os.environ['USERNAME'],
            'Created': str(pd.datetime.now()).partition('.')[0],
            'PyFair Version': VERSION,
            'Type': type(self).__name__
        }).to_frame().to_html(border=0, header=None, justify='left', classes='fair_metadata_table')
        report = report.replace('{METADATA}', metadata)


        

        # Return report
        return report