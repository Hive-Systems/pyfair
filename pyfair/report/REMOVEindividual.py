import pandas as pd

from .report_base import FairBaseReport


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
        metadata = self._get_metadata_table()
        report = report.replace('{METADATA}', metadata)

        # Drawing
        

        # Return report
        return report