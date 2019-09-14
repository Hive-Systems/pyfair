"""Model defining a model creator for similar iterations on models"""

from ..model.model import FairModel


class FairModelFactory(object):
    """A convenience class for creating small variations on models.

    Generally this is used for creating two or more models with slight
    variations.

    Parameters
    ----------
    static_arguments : dict
        A dictionary that has keys of the pyfair nodes, and values of
        dictionaries containing the distribution arguments for that node
    n_simulations : int, optional
        Number of simulations created (default is 10,000)
    random_seed : int, optional
        Random seed for number generation (default is 42)

    """
    def __init__(self, static_arguments, n_simulations=10_000, random_seed=42):
        self._static_arguments = static_arguments
        self._n_simulations = n_simulations
        self._random_seed = random_seed

    def generate_from_partial(self, name, variable_arguments):
        """Generate model from name and set of partial parameters

        The factory instance will have a set of static parameters. By
        passing a name and set of variable arguments, it is possible to
        obtain a new model.

        Parameters
        ----------
        name : str
            The name to assign to the new model
        variable_arguments : dict
            Dictionary with target nodes as the keys and dictionaries of
            arguments for those keys as the values

        Returns
        -------
        FairModel
            A model with the appropriate name and values from both the
            static arguments and the variable arguments

        Raises
        ------
        FairException
            If parameters are insufficient for underlying model creation

        Examples
        --------
        >>> fac = FairModelFactory({
        ...    'Loss Magnitude': {'constant': 5_000_000}
        ... })
        >>> model1 =  fac.generate_from_partial(
        ...     'model1',
        ...    {'Loss Event Frequency': {'constant': 900}}
        ... )
        >>> model2 =  fac.generate_from_partial(
        ...     'model2',
        ...    {'Loss Event Frequency': {'constant': 10}}
        ... )

        """
        # Gen model
        model = FairModel(name, self._n_simulations, self._random_seed)
        # For each group of arguments, run function.
        for argument_group in [self._static_arguments, variable_arguments]:
            self._add_arguments(model, argument_group)
        # Calculate all
        model.calculate_all()
        return model

    def generate_from_partials(self, variable_argument_dict):
        """Generate list of models from a list of partial model parameters

        This simply takes a list of variable dicts and runs
        generate_from_partial() on all of them.

        Parameters
        ----------
        variable_argument_dict : dict
            A dictionary with model names as keys, and parameter
            dictionaries as values. These value dictionaries will have
            target nodes as the keys and dictionaries of arguments for
            those keys as the values

        Returns
        -------
        list of FairModels
            A list of FairModels corresponding with the arguments provided
            as a dict

        Raises
        ------
        FairException
            If parameters are insufficient for underlying model creation

        Examples
        --------
        >>> fac = FairModelFactory({'Loss Magnitude': {'constant': 500}})
        >>> param_list = {
        ...    'model_1': {'Loss Event Frequency': {'constant': 900}},
        ...    'model_2': {'Loss Event Frequency': {'constant': 10}},
        ...    'model_3': {'Loss Event Frequency': {'constant': 9}},
        ... }
        >>> models = fac.generate_from_partials(param_list)

        """
        # Create a list of models based on variable args
        model_list = [
            self.generate_from_partial(name, args)
            for name, args
            in variable_argument_dict.items()
        ]
        # Calculate
        for model in model_list:
            model.calculate_all()
        return model_list

    def _add_arguments(self, model, argument_group):
        """Iterate through arguments and input them into the model"""
        # Go through arguments
        for arg_name, arg_value in argument_group.items():
            # If it's multi, run input_multi_data()
            if arg_name.startswith('multi_'):
                model.input_multi_data(arg_name, **arg_value)
            # If regular, run input_data()
            else:
                model.input_data(arg_name, **arg_value)                
        return model
