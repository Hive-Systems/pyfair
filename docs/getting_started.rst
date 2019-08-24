Generally
=========

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















Getting Started
===============

Usage
-----

This section relates to how to use pyfair. If you are not familiar with the
FAIR methodology, please skip to "Generally"<LINK TODO>. It covers the Main
API objects that are most commonly used.

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
models, from a database, uploading groups of parameters at the same time)
... the general approach will almost always be the same. You will create 
the model, you will input your data, and you will calculate your model 
before using the results.

Pyfair will take care of most of the "under the hood" unpleasantness
associated with the Monte Carlo generation and FAIR calculation. You simply
supply the targets and the distribution types (mean/stdev for normal,
low/mode/high for BetaPert, constant for constants, and p for binomial). 

If you don't supply the right nodes to create a proper calculation, pyfair
will tell you what you're missing. If you don't supply the right arguments,
pyfair will tell you. Et cetera, et cetera, et cetera.

FairMetaModel
~~~~~~~~~~~~~

At times you will likely want to determine what the total amount of risk is
for a number of FairModels. Rolling these model risks up into a single unit
is what the FairMetaModel<TODO LINK> does. These can be created in a number
 of ways, but most generally you will simply feed a list of FairModels to a
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

Related to the metamodel is the FairModelFactor object <TODOLINK>. Often
you will want to create a group of models that are identical except for one
or two minor differences. For example, if you want to create a model for an
entire threat community, you may wish to create a model for "Threat Group
1", "Threat Group 2", and "Threat Group 3" before aggregating the risk into
a single metamodel. FairModelFactory allows this by taking the parameters
that will not change, and then putting in a list of the parameters that
will change. An example is below:

.. code-bock:: python

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

FairDatabase
~~~~~~~~~~~~

The FairDatabase object <TODO CONTENT> exists to store models so that they
can be loaded at a later date. For the sake of space, pyfair does not store
all model results. Rather it stores parameters for simulations, which are
run anew each time. Though because the random seeds for your random number
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

Frequently Asked Questions (FAQs)
=================================

Why do the parameters I use throw errors?
-----------------------------------------

Because of the structure of the FAIR process, it is not possible to use
each and every argument type and value. Here are some of the common
problems:

Value Range
~~~~~~~~~~~

General rules:
* No argument can be less than 0

The following nodes must have values from 0 to 1:
* TC: Threat Capability
* CS: Control Strength
* A: Action

The following nodes must have a value of exactly 0 or 1:
* V: Vulnerability

Pert distributions:
* High parameter must be equal to or greater than Mode parameter
* Mode parameter must be equal to or greater than Low parameter

Vulnerability
~~~~~~~~~~~~~

Vulnerability is weird. It can only be calculated via a step function, and
can only be assigned using the "p" keyword. Because Vulnerability can only
be either a 0 or a 1, a Bernoulli distribution is used with the Probability
of activation being determined by the "p" keyword argument.

Parameter Mismatch
------------------

Keywords must be used as follows:
* constant: must be the only parameter used for a given node
* p: may only be used for Vulnerability
* low, mode, and high: must be used together (gamma is optional)
* mean, stdev: must be used together

Why are my calculation dependencies unresolved?
-----------------------------------------------

pyfair uses the following structure for calculations: <TODO LEAF NODE BRANCH TREE>

As you can see, this takes the form of tree composed of nodes. A the
bottom there are "leaf" nodes. These nodes can only be supplied with data
and cannot be calculated from other values. At the top there is the "root"
node representing a dollar value for Risk. It can only be calculated
(after all, that is the point of the FAIR exercise). In the middle, we have
"branch" nodes. These nodes can either be supplied with values, or
calculated if both of the items beneath it have been supplied or
calculated. By extension, that means that you need not supply any
information on nodes that fall underneath.

This is clearer when looking at an example. Say you run the following code:

.. code-block:: python

    from pyfair import FairModel
    

    # Create an incomplete model
    model = FairModel('Tree Test')
    model.input_data('Loss Event Frequency', mean=5, stdev=1)
    model.calculate_all()
    
Your code will raise this error:

.. code-block::

    FairException: Not ready for calculation. See statuses: 
    Risk                                  Required
    Loss Event Frequency                  Supplied
    Threat Event Frequency            Not Required
    Contact                           Not Required
    Action                            Not Required
    Vulnerability                     Not Required
    Control Strength                  Not Required
    Threat Capability                 Not Required
    Loss Magnitude                        Required
    Primary Loss                          Required
    Secondary Loss                        Required
    Secondary Loss Event Frequency        Required
    Secondary Loss Event Magnitude        Required

THe reason for this is readily apparent when looking at the calculation
tree:

<TODO TREE GIF ONLY LEF>

As you can see, you supplied "Loss Event Frequency". That means you do not
need to calculate "Loss Event Frequency" ... and you also don't have to
deal with anything underneath it because it's all superfluous. That said,
you cannot calculate RIsk because the whole right side of the FAIR
calculation hasn't been supplied.

If you were create a new model with "Loss Magnitude" and "Loss Event
Frequency" you'd cover both branches of the FAIR model and would receive
no error. Notice that you did not have to supply information for everything
in the error above. Pyfair lists them all as required because it has no
idea what you're going to put in next (and so it doesn't know whether it
will be high on the tree or low on the tree).

This gets slightly more complex if you have multiple inputs, but luckily
pyair is smart enough to sort out most stuff:

<TODO PUT IN COMPLEX EXAMPLE>

Why do my simulation results change from run to run?
----------------------------------------------------

Monte Carlo simulations are an attempt to harness large numbers of random
simulations to model complex outcomes. pyfair seeds its random number
generation with a so-called "random seed". This makes the outcome, While
quasi-random and suitable for modeling, actually deterministic in fact. As
a consequence, we can run a pyfair simulation today and a simulation
tomorrow, and they will come out the same if the parameters are the same.

By default, the random seed is 42. If you're reading this, you've probably
changed the random seed.
