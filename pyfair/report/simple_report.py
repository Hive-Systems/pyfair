import pandas as pd

from .base_report import FairBaseReport


class FairSimpleReport(FairBaseReport):
    
    def __init__(self, model_or_models):
        super().__init__()
        self._model_or_models = self._input_check(model_or_models)
        self._css = self._template_paths['css'].read_text()
        self._template = self._template_paths['simple'].read_text()
        
    def _construct_output(self):
        """HTML creation Ffnction called by FairBaseReport.to_html()"""
        
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
        hist = self._get_distribution(self._model_or_models.values())
        t = t.replace('{HIST}', hist)
        
        # Overview Exceedence Curves
        exceed = self._get_exceedence_curves(self._model_or_models.values())
        t = t.replace('{EXCEEDENCE}', exceed)
        
        # Create parameter html
        parameter_html = ''
        for name, model in self._model_or_models.items():
            parameter_html += "<h1>{}</h1>".format(name)
            parameter_html += "<div class='flex_row'>"

            # Create images which differ based on type
            if model.__class__.__name__ == 'FairModel':
                parameter_html += self._get_tree(model)
            if model.__class__.__name__ == 'FairMetaModel':
                parameter_html += self._get_violins(model)
            
            parameter_html += "</div>"
            
            # Create table
            parameter_html += "<div class='flex_row'>"
            
            # Create tables which differ based on type
            if model.__class__.__name__ == 'FairModel':
                parameter_html += self._get_model_parameter_table(model)
            if model.__class__.__name__ == 'FairMetaModel':
                parameter_html += self._get_metamodel_parameter_table(model)

            parameter_html += "</div><br>"

        # TODO Text wrap
        t = t.replace('{PARAMETER_HTML}', parameter_html)
        
        # JSON and Source
        json = ''
        for name, model in self._model_or_models.items():
            json += name
            json += '\n====================\n'
            json += model.to_json()
            json += '\n\n\n'
        t = t.replace('{JSON}', json)
        source = self._get_caller_source()
        source.replace('<', '').replace('>','')
        t = t.replace('{SOURCE}', source)
        
        return t