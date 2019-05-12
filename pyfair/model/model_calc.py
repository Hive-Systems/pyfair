class FairCalculations(object):
    '''A class to perform calculations'''
    
    def __init__(self):
        self._data = None
        # Lookup table (no leaf nodes required)
        self._function_dict = {
            'Risk'                       : self._calculate_addition,
            'Loss Event Frequency'       : self._calculate_multiplication,
            'Threat Event Frequency'     : self._calculate_multiplication,
            'Vulnerability'              : self._calculate_step,
            'Probable Loss Magnitude'    : self._calculate_addition,
            'Primary Loss Factors'       : self._calculate_multiplication,
            'Threat Loss Factors'        : self._calculate_multiplication,
            'Secondary Loss Factors'     : self._calculate_multiplication,
        }

    def calculate(self, parent_name, child_1_data, child_2_data):
        '''General function for dispatching calculations'''
        target_function = self._function_dict[parent_name]
        calculated_result = target_function(parent_name, child_1_data, child_2_data)
        return calculated_result
    
    def _calculate_step(self, parent_name, child_1_data, child_2_data):
        '''Create a bool series, which can be multiplied as 0/1 value'''
        return child_1_data > child_2_data
    
    def _calculate_addition(self, parent_name, child_1_data, child_2_data):
        '''Calculate sum of two columns'''
        return child_1_data + child_2_data
    
    def _calculate_multiplication(self, parent_name, child_1_data, child_2_data):
        '''Calculate product of two columns'''
        return child_1_data * child_2_data
