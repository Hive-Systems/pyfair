'''PyFair is an open-source implementation of the Factor Analysis of Information Risk (FAIR) methodology.'''

VERSION = '0.1.0'


from . import model
from . import report
from . import utility

from .model.model import FairModel
from .model.meta_model import FairMetaModel
from .utility.beta_pert import FairBetaPert
from .report.simple_report import FairSimpleReport
