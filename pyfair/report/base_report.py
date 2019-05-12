class FairBaseReport(object):
    '''A base report class with boilerplate.'''

    def __init__(self, fair_model=None):
        self._fair_model = fair_model
        raise NotImplementedError()
    
    def load_model(self, model):
        self._fair_model = model

    def to_pdf(self, path):
        pass

