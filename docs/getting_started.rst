Getting Started With pyfair
===========================

Usage
-----

This section relates to how to use pyfair.

In general you will supply your inputs, calculate your model, and then do
something with the data (e.g. store it, create a report, or feed it into
another calcluation).

Here is how you can use these pyfair tools to do that.

FairModel
~~~~~~~~~

The most basic element of PyFair is the FairModel. This
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

.. note::

    pyfair uses pandas heavily for data manipulation, and consequently your 
    results will be exported as easy-to-manipulate DataFrames unless 
    otherwise specified.

While there are various ways to create these models (from serialized JSON
models, from a database, uploading groups of parameters at the same time)
... the general approach will almost always be the same. You will create 
the model, you will input your data, and you will calculate your model 
before using the results.

pyfair will take care of most of the "under the hood" unpleasantness
associated with the Monte Carlo generation and FAIR calculation. You simply
supply the targets and the distribution types. These targets are:

    * BetaPert: low, mode, and high (and optionally gamma)
    * Constant: constant
    * Normal: mean, stdev

.. warning::

    You cannot mix these parameters. If you give a function a "constant"
    parameter, a "low" parameter, and a "mean" parameter, it will throw an
    error.

If you don't supply the right nodes to create a proper calculation, pyfair
will tell you what you're missing. If you don't supply the right arguments,
pyfair will tell you. Et cetera, et cetera, et cetera.

FairMetaModel
~~~~~~~~~~~~~

At times you will likely want to determine what the total amount of risk is
for a number of FairModels. Rolling these model risks up into a single unit
is what the FairMetaModel does. These can be created in a number of ways,
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
    metamodel = FairMetaModel(name='Our MetaModel', models=[model1, model2])

    # Calclate our MetaModel (and contained Models)
    metamodel.calculate_all()

    # Export results
    metamodel.export_results()

Again, the general workflow is the same. We create our metamodel, we
calculate our data, and we export the results.

FairModelFactory
~~~~~~~~~~~~~~~~

Related to the metamodel is the FairModelFactory object. Often you will
want to create a group of models that are identical except for one or two 
minor differences. For example, if you want to create a model for an entire
threat community, you may wish to create a model for "Threat Group 1", 
"Threat Group 2", and "Threat Group 3" before aggregating the risk into a 
single metamodel. FairModelFactory allows this by taking the parameters
that will not change, and then putting in a list of the parameters that
will change. An example is below:

.. code-block:: python

    from pyfair import FairMetaModel, FairModelFactory


    # Instantiate factory
    factory = FairModelFactory({'Loss Magnitude': {'constant': 5_000_000}})

    # Create 3 models with variable arguments
    state_actor = factory.generate_from_partial(
        'Nation State',
        {'Threat Event Frequency': {'mean': 50, 'stdev': 5}, 'Vulnerability': {'p': .95}}
    )
    hacktivist = factory.generate_from_partial(
        'Hactivist',
        {'Threat Event Frequency': {'mean': 5_000, 'stdev': 10}, 'Vulnerability': {'p': .25}}
    )
    id_thief = factory.generate_from_partial(
        'Identity Thief',
        {'Threat Event Frequency': {'mean': 500, 'stdev': 100}, 'Vulnerability': {'p': .75}}
    )

    # Create a metamodel
    meta = FairMetaModel('Aggregate', [state_actor, hacktivist, id_thief])
    meta.calculate_all()
    results = meta.export_results()

FairSimpleReport
~~~~~~~~~~~~~~~~

The FairSimpleReport is a mechanism to create a basic HTML-based report. It 
can take Models, MetaModels, or a list of Models and MetaModels like so:

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

FairDatabase
~~~~~~~~~~~~

The FairDatabase object exists in order to store models so that they can
be loaded at a later date. For the sake of space, pyfair does not store all 
model results. Rather it stores parameters for simulations, which are run 
anew each time. Though because the random seeds for your random number
generation stay the same, your results will be reproducible. This works as
follows:

.. code-block:: python

    from pyfair import FairModel, FairDatabase


    # Create a model
    model = FairModel('2019 Simulation')
    model.bulk_import_data({
        'Loss Event Frequency': {'mean':.3, 'stdev':.1},
        'Loss Magnitude': {'constant': 5_000_000}
    })
    model.calculate_all()
    
    # Create a database file and store a model
    db = FairDatabase('pyfair.sqlite3')
    db.store(model)
    
    # Load a model
    reconstituted_model = db.load('2019 Simulation')
    reconstituted_model.calculate_all()
