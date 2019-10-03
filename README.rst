pyfair
======

.. image:: static/logo.PNG
    :alt: logo
    :width: 200px

.. image:: https://readthedocs.org/projects/pyfair/badge/?version=latest
    :alt: Doc Badge

 .. image:: https://travis-ci.org/theonaunheim/pyfair.svg?branch=master
    :alt: Buid Badge

Factor Analysis of Information Risk (FAIR) model written in Python.

This package endeavors to create a simple API for automating the creation
of
`FAIR <https://en.wikipedia.org/wiki/Factor_analysis_of_information_risk/>`_
Monte Carlo risk simulations.

This is based in large part on:

1. the `Open FAIR™ Technical Standard published by the Open Group <http://pubs.opengroup.org/onlinepubs/9699919899/toc.pdf/>`_; and,
2. `Measuring and Managing Information Risk <https://www.amazon.com/Measuring-Managing-Information-Risk-Approach-ebook/dp/B00N9YPW5C/>`_

"Open FAIR" is a trademark of the Open Group.

Installation
------------

pyfair is available on `PyPI <https://pypi.org/project/pyfair/>`_. To use 
pyfair with your Python installation, you can run:

.. code-block:: python

    pip install pyfair

Documentation
-------------

Documentation can be found at the
`Read the Docs site <https://pyfair.readthedocs.io/en/latest/>`_.

Code
----

.. code-block:: python

    import pyfair

    # Create using LEF (PERT), PL, (PERT), and SL (constant)
    model1 = pyfair.FairModel(name="Regular Model 1", n_simulations=10_000)
    model1.input_data('Loss Event Frequency', low=20, mode=100, high=900)
    model1.input_data('Primary Loss', low=3_000_000, mode=3_500_000, high=5_000_000)
    model1.input_data('Secondary Loss', constant=3_500_000)
    model1.calculate_all()

    # Create another model using LEF (Normal) and LM (PERT)
    model2 = pyfair.FairModel(name="Regular Model 2", n_simulations=10_000)
    model2.input_data('Loss Event Frequency', mean=.3, stdev=.1)
    model2.input_data('Loss Magnitude', low=2_000_000_000, mode=3_000_000_000, high=5_000_000_000)
    model2.calculate_all()

    # Create metamodel by combining 1 and 2
    mm = pyfair.FairMetaModel(name='My Meta Model!', models=[model1, model2])
    mm.calculate_all()

    # Create report comparing 2 vs metamodel.
    fsr = pyfair.FairSimpleReport([model1, mm])
    fsr.to_html('output.html')

Report Output
-------------

.. image:: static/overview.PNG
    :alt: Overview

.. image:: /static/tree.PNG
    :alt: Tree

.. image:: static/violin.PNG
    :alt: Violin

Serialized Model
----------------

.. code-block:: json

    {
        "Loss Event Frequency": {
            "low": 20,
            "mode": 100,
            "high": 900
        },
        "Loss Magnitude": {
            "low": 3000000,
            "mode": 3500000,
            "high": 5000000
        },
        "name": "Regular Model 1",
        "n_simulations": 10000,
        "random_seed": 42,
        "model_uuid": "b6c6c968-a03c-11e9-a5db-f26e0bbd6dbc",
        "type": "FairModel",
        "creation_date": "2019-07-06 17:23:43.647370"
    }
