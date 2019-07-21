import pathlib
import sys
import unittest

# Add pyfair directory to path
this_file = pathlib.Path(__file__).absolute()
repo_dir  = this_file.parents[1]
path      = str(repo_dir)
sys.path.append(path)

# Import test modules
import model.test_model
import model.test_model_tree
import model.test_model_node

# List test modules
test_modules = [
    model.test_model,
    model.test_model_tree,
    model.test_model_node,
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