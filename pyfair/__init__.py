"""PyFair is an open source implementation of the FAIR methodology."""

<<<<<<< HEAD
VERSION = '0.2-beta.0'
=======
VERSION = '0.1-alpha.12'
>>>>>>> master


from . import model
from . import report
from . import utility

from .model.model import FairModel
from .model.meta_model import FairMetaModel
from .report.simple_report import FairSimpleReport
from .utility.beta_pert import FairBetaPert
from .utility.database import FairDatabase
from .utility.factory import FairModelFactory
