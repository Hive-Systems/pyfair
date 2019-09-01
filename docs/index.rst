.. pyfair documentation master file, created by
   sphinx-quickstart on Tue Jul 16 06:48:49 2019.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to pyfair's documentation!
==================================

.. contents:: Table of Contents
   :depth: 1

.. include:: getting_started.rst

Model Classes
=============

FairModel
-------------

.. autoclass:: pyfair.model.model.FairModel
    :members:

FairMetaModel
-------------

.. autoclass:: pyfair.model.meta_model.FairMetaModel 
    :members:

FairCalculations
-------------

.. autoclass:: pyfair.model.model_calc.FairCalculations
    :members:

FairDataInput
-------------

.. autoclass:: pyfair.model.model_input.FairDataInput
    :members:

FairDependencyNode
-------------

.. autoclass:: pyfair.model.model_node.FairDependencyNode
    :members:

FairDependencyTree
-------------

.. autoclass:: pyfair.model.model_tree.FairDependencyTree
    :members:

Report Classes
==============

FairSimpleReport
-------------

.. autoclass:: pyfair.report.simple_report.FairSimpleReport
    :members:
    :inherited-members:

FairBaseReport
-------------

.. autoclass:: pyfair.report.base_report.FairBaseReport
    :members:

FairBaseCurve
-------------

.. autoclass:: pyfair.report.base_curve.FairBaseCurve
    :members:

FairDistributionCurve
-------------

.. autoclass:: pyfair.report.distribution.FairDistributionCurve
    :members:
    :inherited-members:

FairExceedenceCurves
-------------

.. autoclass:: pyfair.report.exceedence.FairExceedenceCurves
    :members:
    :inherited-members:

FairTreeGraph
-------------

.. autoclass:: pyfair.report.tree_graph.FairTreeGraph
    :members:

FairViolinPlot
-------------

.. autoclass:: pyfair.report.violin.FairViolinPlot
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
-------------

.. autoclass:: pyfair.utility.parser.FairSimpleParser
    :members:

FairModelFactory
-------------

.. autoclass:: pyfair.utility.factory.FairModelFactory
    :members:

FairDatabase
-------------

.. autoclass:: pyfair.utility.database.FairDatabase
    :members:

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
