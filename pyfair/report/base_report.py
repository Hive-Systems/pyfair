class FairBaseReport(object):
    '''A base report class with boilerplate.'''

    def __init__(self):
        dollar_format_string     = '${0:,}'
        integer_format_string    = '{0:,}'
        percentage_format_string = '{0:.3f}'
        format_strings = {
            'Risk'                        : dollar_format_string,
            'Loss Event Frequency'        : integer_format_string,
            'Threat Event Frequency'      : integer_format_string,
            'Vulnerability'               : integer_format_string,         
            'Contact'                     : percentage_format_string,
            'Action'                      : percentage_format_string,
            'Threat Capability'           : percentage_format_string,
            'Control Strength'            : percentage_format_string,
            'Probable Loss Magnitude'     : dollar_format_string,
            'Primary Loss Factors'        : dollar_format_string,
            'Asset Loss Factors'          : dollar_format_string,
            'Threat Loss Factors'         : dollar_format_string,
            'Secondary Loss Factors'      : dollar_format_string,
            'Organizational Loss Factors' : dollar_format_string,
            'External Loss Factors'       : dollar_format_string,
        }


    def load_model(self, model):
        self._fair_model = model

    def to_pdf(self, path):
        pass

