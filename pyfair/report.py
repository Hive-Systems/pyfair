class FairReport(object):
    '''Wraps a fair report and generates results.'''

    def __init__(self, fair_model=None):
        self._fair_model = fair_model
    
    def load_model(self, model):
        self._fair_model = model

    def to_pdf(self, path):
        pass


class FairTemplateParser(object):

    def __init__(self):
        raise NotImplementedError()


class FairControlReview(object):
    '''A report comparing unmitigated risks vs. mitigated risks'''

    def __init__(self):
        raise NotImplementedError()


class FairMetaModelReport(object):
    '''A report for multiple actors'''

    def __init__(self):
        raise NotImplementedError()