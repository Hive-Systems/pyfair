import pathlib
import sys
import unittest

# Add pyfair directory to path
this_file = pathlib.Path(__file__).absolute()
repo_dir  = this_file.parents[1]
path      = str(repo_dir)
sys.path.append(path)

# Import test modules
import model.test_meta_model
import model.test_model_calc
import model.test_model_input
import model.test_model_node
import model.test_model_tree
import model.test_model


# List test modules
test_modules = [
    # Model Module
    model.test_meta_model,
    model.test_model_calc,
    model.test_model_input,
    model.test_model_node,
    model.test_model_tree,
    model.test_model,
    # Report Module
    #report.base_curve,
    #report.base_report,
    #report.distribution,
    #report.exceedence,
    #report.simple_report,
    #report.tree_graph,
    #report.violin,
    # Utility Module
    #utility.beta_pert,
    #utility.database,
    #utility.factory,
    #utility.fair_exception,
    #utility.parser
]

# Create loader and suite
loader = unittest.TestLoader()
suite  = unittest.TestSuite()

# Add to suite
for test_module in test_modules:
    loaded_test = loader.loadTestsFromModule(test_module)
    suite.addTest(loaded_test)

# Create runner and run
runner = unittest.TextTestRunner(verbosity=5)
result = runner.run(suite)