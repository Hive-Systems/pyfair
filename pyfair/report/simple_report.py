"""Simple report for demonstrating aggregate risk"""

import pandas as pd

from .base_report import FairBaseReport


class FairSimpleReport(FairBaseReport):
    """A subclass for creating the report HTML

    This class is responsible for implementing the _construct_output()
    method. The method is takes the template and css for the simple report
    and plugs in the appropriate data base on the models supplied.

    Parameters
    ----------
    currency_prefix : str
        The currency symbol in front of your (default: $)

    Examples
    --------
    >>> m1 = pyfair.model.FairModel.from_json('model_1.json')
    >>> m2 = pyfair.model.FairModel.from_json('model_2.json')
    >>> fsr = FairSimpleReport([m1, m2], currency_prefix='元')
    >>> fsr.generate_html('output.html')

    """
    def __init__(self, model_or_models, currency_prefix='$'):
        super().__init__(currency_prefix=currency_prefix)
        self._currency_prefix = currency_prefix
        self._model_or_models = self._input_check(model_or_models)
        self._css = self._template_paths['css'].read_text()
        self._template = self._template_paths['simple'].read_text()

    def _construct_output(self):
        """HTML creation function called by FairBaseReport.to_html()

        This is responsible for creating all of the HTML for a given report
        type.

        """
        # Alias
        t = self._template
        # Add css
        t = t.replace('{STYLE}', self._css)
        # Add Metadata
        t = t.replace('{METADATA}', self._get_metadata_table())
        # Get logo tag
        b64 = self.base64ify(self._logo_location)
        t = t.replace('{PYTHON_LOGO}', b64)

        # Overview Table
        overview_html = self._get_overview_table(self._model_or_models)
        t = t.replace('{OVERVIEW_DATAFRAME}', overview_html)

        # Overview Hist
        hist = self._get_distribution(
            self._model_or_models.values(), 
            currency_prefix=self._currency_prefix
        )
        t = t.replace('{HIST}', hist)

        # Overview Exceedence Curves
        exceed = self._get_exceedence_curves(
            self._model_or_models.values(), 
            currency_prefix=self._currency_prefix
        )
        t = t.replace('{EXCEEDENCE}', exceed)

        # Create parameter html
        parameter_html = ''
        for name, model in self._model_or_models.items():
            parameter_html += "<h1>{}</h1>".format(name)

            # Create images which differ based on type
            if model.__class__.__name__ == 'FairModel':
                parameter_html += self._get_tree(model)
            if model.__class__.__name__ == 'FairMetaModel':
                parameter_html += self._get_violins(model)
                
            # Create table

            # Create tables which differ based on type
            if model.__class__.__name__ == 'FairModel':
                parameter_html += self._get_model_parameter_table(model)
            if model.__class__.__name__ == 'FairMetaModel':
                parameter_html += self._get_metamodel_parameter_table(model)

            parameter_html += "<br>"

        # TODO Text wrap
        t = t.replace('{PARAMETER_HTML}', parameter_html)

        return t
