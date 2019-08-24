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

.. include:: getting_started.rst

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
