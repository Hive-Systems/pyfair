import pathlib
import sys

# Get repo directory
this_file = pathlib.Path(__file__).absolute()
repo_dir  = this_file.parents[1]
path      = str(repo_dir)

# Get data directory
data_directory = repo_dir / 'tests' / 'data'

# Append directory to path.
sys.path.append(path)

import pyfair
