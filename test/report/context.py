import pathlib
import sys

# Get repo directory
this_file = pathlib.Path(__file__).absolute()
repo_dir  = this_file.parents[2]
path      = str(repo_dir)

# Append directory to path.
sys.path.append(path)

import pyfair
