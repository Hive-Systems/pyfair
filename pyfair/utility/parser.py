import xlrd

import pandas as pd

from pyfair.model.meta_model import FairMetaModel
from pyfair.model.model import FairModel
from pyfair.report.simple_report import FairSimpleReport
from pyfair.utility.fair_exception import FairException


class FairSimpleParser(object):
    '''Horific parser.'''
    
    def __init__(self, workbook_path):
        raise NotImplementedError()
        self._path          = workbook_path
        self._names         = list()
        self._raw_data      = dict()
        self._n_simulations = None
        self._random_seed   = None
        self._output_path   = None
        self._data          = dict()
        self._models        = dict()
        self._metamodels    = dict()
        self._populate_object()
        self._split_frames()
        self._convert_to_models()
        self._create_metamodels()
    
    def to_html(self, path):
        metamodels = [item for item in self._metamodels.values() if item is not None]
        if metamodels:
            fsr = FairSimpleReport(metamodels)
            fsr.to_html(path)
        else:
            raise FairException('Template is missing data.')
    
    def export_metamodels(self):
        return [item for item in self._metamodels.values()]
    
    def _create_metamodels(self):
        '''Create the metamodels'''
        for metamodel_name, model_list in self._models.items():
            if model_list:
                metamodel = FairMetaModel(
                    name=metamodel_name,
                    models=model_list
                )
                metamodel.calculate_all()
                self._metamodels[metamodel_name] = metamodel
            else:
                self._metamodels[metamodel_name] = None
    
    def _populate_object(self):
        '''Read sheet data into two huge frames'''
        # Read workbook
        wb = xlrd.open_workbook(self._path)
        # Create sheets via list comprehension
        self._names  = wb.sheet_names()
        # For tabs two and three
        for name in self._names[1:]:
            df = pd.read_excel(self._path, sheet_name=name)
            self._raw_data[name] = df
        # For tab 1
        df = pd.read_excel(self._path, sheet_name=self._names[0])
        # These should fail catastrophically if unpopulated.
        self._n_simulations = int(df.iloc[0, 1])
        self._random_seed = int(df.iloc[1, 1])
        self._output_path = df.iloc[2, 1]

    def _split_frames(self):
        '''For each of the main frames into components and store'''
        # For each big frame
        for designation, big_frame in self._raw_data.items():
            # Run the parse frame operation on the big frame
            rv = self._parse_raw_frame(big_frame)
            # Split rv into names, primary, and secondary
            model_names, primary_params, secondary_params = rv
            # Store as dict of dicts
            self._data[designation] = {
                'names'           : model_names,
                'primary_params'  : primary_params,
                'secondary_params': secondary_params,
            }
            
    def _convert_to_models(self):
        for designation, data in self._data.items():
            model_list = []
            for i in range(10):
                target         = self._data[designation]
                # ILOC because pandas is giving a weird error
                name           = target['names'][i]
                raw_pri_params = target['primary_params'][i]
                raw_sec_params = target['secondary_params'][i]
                # Alias
                cdtpd = self._convert_df_to_param_dict
                # Run function
                ref_pri_params = cdtpd(raw_pri_params)
                ref_sec_params = cdtpd(raw_sec_params)
                ref_sec_params = {''.join('multi_', key): value for key, value in ref_sec_params.items()}
                # Create model
                if ref_pri_params:
                    model = FairModel(
                        name, 
                        n_simulations=self._n_simulations, 
                        random_seed=self._random_seed,
                    )
                    if ref_pri_params:
                        model.bulk_import_data(ref_pri_params)
                    if ref_sec_params:
                        model.input_multi_data('Secondary Loss Event Magnitude', ref_sec_params)
                    # Calculate
                    model.calculate_all()
                    model_list.append(model)
                else:
                    pass
            self._models[designation] = model_list
                
    def _parse_raw_frame(self, df):
        '''Take the raw data from the Excel sheet and generate 1 series and 2 frames'''
        # Groups of 12
        gb = df.groupby(df.index.values // 12)
        # Get names
        dfs = [gb.get_group(group) for group in gb.groups]
        names = [self._get_model_name(df) for df in dfs]
        primary = [self._get_model_primary_params(df) for df in dfs]
        secondary = [self._get_model_secondary_params(df) for df in dfs]
        return (names, primary, secondary)

    def _get_model_name(self, df):
        '''Via gb.apply(): get model names'''
        name = df.iloc[0,1]
        return name

    def _get_model_primary_params(self, df):
        '''Via gb.apply(): drop last two rows from each entry, get columns low through constant'''
        main_df = df.iloc[:-2, 3:12]
        main_df = main_df.set_index('Target Name')
        return main_df

    def _get_model_secondary_params(self, df):
        '''Via gb.apply(): drop last rows from each entry, get columns Loss Name through SLEM'''
        # Chop down to 
        secondary_df = df.iloc[:-2, 13:16]
        secondary_df = secondary_df.set_index('Loss Name')
        return secondary_df

    def _convert_df_to_param_dict(self, df):
        ''' Convenience function to convert dataframe to dict.
        Converts: 
        
            pd.DataFrame({
                    'col_1': ['a'   , 'b', np.NaN],
                    'col_2': [np.NaN, 'c', np.NaN]
                },
                index=['row_1', 'row_2', 'row_3']
            )

        To:
        
            {
                'row_1': {'col_1': 'a'}, 
                'row_2': {'col_1': 'b', 'col_2': 'c'}
            }
        '''
        # Drop all rows without entries
        df = df.dropna(how='all', axis=0)
        # Make a dict from each row of params, dropping empty entries
        param_series = df.apply(lambda row: row.dropna().to_dict(), axis=1)
        # Make a dict from that series of dicts, giving us out multidimensional dict
        rv_dict = param_series.to_dict()
        return rv_dict   
