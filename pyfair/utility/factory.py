from ..model.model import FairModel


class FairModelFactory(object):
    '''This is a convenience class for creating small variations on models.'''

    def __init__(self, static_arguments, n_simulations=10_000, random_seed=42):
        self._static_arguments = static_arguments
        self._n_simulations    = n_simulations
        self._random_seed      = random_seed
    
    def generate_from_partial(self, name, variable_arguments):
        '''Provide partial parameters.'''
        # Gen model
        model = FairModel(name, self._n_simulations, self._random_seed)
        # For each group of arguments, run function.
        for argument_group in [self._static_arguments, variable_arguments]:
            self._add_arguments(model, argument_group)
        # Calculate all
        model.calculate_all()
        return model

    def generate_from_partials(self, variable_argument_dict):
        '''Provide partial parameters as a dictionary'''
        # Create a list of models based on variable args
        model_list = [
            self.generate_from_partial(name, args)
            for name, args
            in variable_argument_dict.items()
        ]
        # Caculate
        for model in model_list:
            model.calculate_all()
        return model_list
        
    def _add_arguments(self, model, argument_group):
        # Go through arguments
        for arg_name, arg_value in argument_group.items():
            # If it's multi, run input_multi_data()
            if arg_name.startswith('multi_'):
                model.input_multi_data(arg_name, **arg_value)
            # If regular, run input_data()
            else:
                print(arg_value)
                model.input_data(arg_name, **arg_value)                
        return model
