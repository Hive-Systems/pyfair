.. pyfair documentation master file, created by
   sphinx-quickstart on Tue Jul 16 06:48:49 2019.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to pyfair's documentation!
==================================

.. toctree::
   :maxdepth: 2
   :caption: Contents:

.. contents:: Table of Contents

Getting Started
===============

Usage
-----

This section relates to how to use pyfair. If you are not familiar with the
FAIR methodology, please skip to "Generally"<LINK TODO>

FairModel
~~~~~~~~~

The most basic element of PyFair is the FairModel <LINK TODO>. This
FairModel is used to create basic Monte Carlo simulations as follows:

.. code-block:: python

    from pyfair import FairModel


    # Create our model
    model = FairModel(name='Basic Model', n_simulations=10_000)

    # Add normally distributed data
    model.input_data('Loss Event Frequency', mean=.3, stdev=.1)

    # Add constant data
    model.input_data('Loss Magnitude', constant=5_000_000)

    # We could hypothetically do BetaPert data
    # model.input_data('Loss Magnitude', low=0, mode=10, high=100, gamma=90)

    # Run our simulations
    model.calculate_all()

    # Export results (if desired)
    results = model.export_results()

To reiterate what we did: first, we created a model object for us to use 
with a name of "Basic Model" and composed of 10,000 simulations. We then
supplied the "Loss Event Frequency" node with 10,000 normally distributed
random data values, and provided 10,000 entries into "Loss Magnitude" of
5,000,000. We then run the calculations for the simulation by running
calculate_all(), after which we can export the results or examine the
object however we wish.

A quick side node: pyfair uses pandas heavily for data manipulation, and
conseqeuntly your results will be exported as easy-to-manipulate DataFrames
unless otherwise specified.

While there are various ways to create these modesl (from serialized JSON
models, from a database, from bulk data uploads) ... the general approach
will almost always be the same. You will create the model, you will input
your data, and you will calculate your model before using the results.

Pyfair will take care of most of the "under the hood" unpleasantness
associated with the Monte Carlo generation and FAIR calculation. You simply
supply the targets and the distribution types (mean/stdev for normal,
low/mode/high for BetaPert, constant for constants, and p for binomial). 

If you don't supply the right nodes to create a proper calculation, pyfair
will tell you. If you don't supply the right arguments, pyfair will tell
you. Et cetera, et cetera, et cetera.

FairMetaModel
~~~~~~~~~~~~~

At times you will likely want to determine what the total amount of risk is
for a number of FairModels. Rolling these model risks up into a single unit
is what the FairMetaModel<TODO LINK> does. These can be created in a number of ways,
but most generally you will simply feed a list of FairModels to a
FairMetaModel constructor like this:

.. code-block:: python

    from pyfair import FairModel, FairMetaModel


    # Create a model
    model1 = FairModel(name='Risk Type 1', n_simulations=10_000)
    model1.input_data('Loss Event Frequency', mean=.3, stdev=.1)
    model1.input_data('Loss Magnitude', constant=5_000_000)

    # Create another model
    model2 = FairModel(name='Risk Type 2', n_simulations=10_000)
    model2.input_data('Loss Event Frequency', mean=.3, stdev=.1)
    model2.input_data('Loss Magnitude', low=0, mode=10_000_000, high=20_000_000)

    # Create our metamodel
    metamodel = FairMetaModel(name='Our MetaModel, models=[model1, model2])

    # Calclate our MetaModel (and contained Models)
    metamodel.calculate_all()

    # Export results
    metamode.export_results()

Again, the general workflow is the same. We create our metamodel, we
calculate our data, and we export the results.

FairSimpleReport
~~~~~~~~~~~~~~~~

The FairSimpleReport <TODO LINK> is a mechanism to create a basic
HTML-based report. It can take Models, MetaModels, or a list of Models and
MetaModels like so:

.. code-block:: python

    from pyfair import FairModel, FairSimpleReport


    # Create a model
    model1 = FairModel(name='Risk Type 1', n_simulations=10_000)
    model1.input_data('Loss Event Frequency', mean=.3, stdev=.1)
    model1.input_data('Loss Magnitude', constant=5_000_000)

    # Create another model
    model2 = FairModel(name='Risk Type 2', n_simulations=10_000)
    model2.input_data('Loss Event Frequency', mean=.3, stdev=.1)
    model2.input_data('Loss Magnitude', low=0, mode=10_000_000, high=20_000_000)

    # Create a report and write it to an output.
    fsr = FairSimpleReport([model1, model2])
    fsr.to_html('output.html')

As a general rule, if you want to add things together, use a MetaModel and
pass it to the report. If you want to compare two things, pass a list of
the two things to the report. Simply create the report, and then output
the report to an HTML document.




Generally
---------

If you are already familiar with FAIR, please skip to "Usage".

`Factor Analysis for Information Risk ("FAIR")
<https://en.wikipedia.org/wiki/Factor_analysis_of_information_risk>`_
is a methodology for analyzing cybersecurity risk by breaking risk
into its individual components. These components can then be measured
or estimated individually, allowing for a quantitiative calculation of
the risk as a whole.

FAIR recognizes the following types of components:

TREE DIAGRAM








FAIR Background
===============

Components
----------
TODO: Tree here.
Risk
Loss Event Frequency
Threat Event Frequency
Vulnerability
Contact Frequency
Probability of Action
Threat Capability
Control Strength
Loss Magnitude
Primary Loss
Secondary Loss Event Frequency
Secondary Loss Event Magnitude


Relationships
-------------




Main API Classes
================

FairModel
---------

.. autoclass:: pyfair.model.model.FairModel 
    :members:

FairMetaModel
-------------

.. autoclass:: pyfair.model.meta_model.FairMetaModel 
    :members:

FairSimpleReport
----------------

.. autoclass:: pyfair.report.simple_report.FairSimpleReport
    :members:

FairDatabase
------------

.. autoclass:: pyfair.utility.database.FairDatabase
    :members:

FairModelFactory
----------------

.. autoclass:: pyfair.utility.factory.FairModelFactory
    :members:

Utility Classes
===============

FairException
-------------

.. autoexception:: pyfair.utility.fair_exception.FairException
    :members:

FairBetaPert
-------------

.. autoclass:: pyfair.utility.beta_pert.FairBetaPert
    :members:

FairSimpleParser
----------------

.. autoclass:: pyfair.utility.parser.FairSimpleParser
    :members:

Model Classes
=============

.. autoclass:: pyfair.model.model_calc.FairCalculations
    :members:

.. autoclass:: pyfair.model.model_input.FairDataInput
    :members:

.. autoclass:: pyfair.model.model_node.FairDependencyNode
    :members:

.. autoclass:: pyfair.model.model_tree.FairDependencyTree
    :members:

Report Classes
==============

.. autoclass:: pyfair.report.base_curve.FairBaseCurve
    :members:

.. autoclass:: pyfair.report.base_report.FairBaseReport
    :members:

.. autoclass:: pyfair.report.distribution.FairDistributionCurve
    :members:

.. autoclass:: pyfair.report.exceedence.FairExceedenceCurves
    :members:

.. autoclass:: pyfair.report.tree_graph.FairTreeGraph
    :members:

.. autoclass:: pyfair.report.violin.FairViolinPlot
    :members:

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
