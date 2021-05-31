"""PyFair is an open source implementation of the FAIR methodology."""

VERSION = '0.2-beta.0'


from . import model
from . import report
from . import utility

from .model.model import FairModel
from .model.meta_model import FairMetaModel
from .report.simple_report import FairSimpleReport
from .report.jupyter import FairJupyterShim
from .utility.beta_pert import FairBetaPert
from .utility.database import FairDatabase
from .utility.factory import FairModelFactory
