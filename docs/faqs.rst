
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
* A: Probability of Action
* V: Vulnerability

Pert distributions:

* High parameter must be equal to or greater than Most Likely parameter
* Most likely parameter must be equal to or greater than Low parameter

Parameter Mismatch
------------------

Keywords must be used as follows:

* constant: must be the only parameter used for a given node
* low, most_likely, and high: must be used together (gamma is optional)
* mean, stdev: must be used together

Functioning example with all nodes and input types
--------------------------------------------------

.. warning::

    If you supply a node, pyfair essentially ignores all your inputs
    underneath that node. E.g. If you supply Loss Event Frequency,
    you Threat Event Frequency and Vulnerability are immaterial. This
    example exists solely for the purpose of giving you examples of
    valid inputs.

.. code-block:: python

    # Model with all nodes specified
    model = FairModel('All Nodes Defined')
    # Contact Frequency: all parameters must be positive numbers
    # Normal curve takes mean and standard deviation
    model.input_data('Contact Frequency', mean=5, stdev=1)
    # Probability of Action: all parameters must be from zero to one
    # Constant takes a single constant value
    model.input_data('Probability of Action', constant=.95)
    # Threat Capability: all parameters must be from zero to one
    # BetaPert takes without lambda/gamma takes a low, most_likely, and high value
    model.input_data('Threat Capability', low=.2, most_likely=.4, high=.9)
    # Control Strength: all parameters must be from zero to one 
    # BetaPert with lambda/gamma also takes a gamma value
    model.input_data('Control Strength', low=.2, most_likely=.4, high=.9, gamma=2)
    # Secondary Loss Event Frequency: all parameters must be a positive number
    model.input_data('Secondary Loss Event Frequency', constant=50)
    # Secondary Loss Event Magnitude: all parameters must be a positive number
    model.input_data('Secondary Loss Event Magnitude',  constant=50)
    # Threat Event Frequency: all parameters must be a positive number
    model.input_data('Threat Event Frequency',  constant=50)
    # Vulnerability: all parameters must be from zero to one
    model.input_data('Vulnerability', constant=.75)
    # Primary Loss: all parameters must be positive numbers
    model.input_data('Primary Loss', constant=50)
    # Secondary Loss: all parameters must be positive numbers
    model.input_data('Secondary Loss',  constant=50)
    # Secondary Loss Event Frequency: all parameters must be positive numbers
    model.input_data('Loss Event Frequency', constant=50)
    # Loss Magnitude: all parameters must be positive numbers
    model.input_data('Loss Magnitude',  constant=50)
    model.calculate_all()

Why are my calculation dependencies unresolved?
-----------------------------------------------

pyfair uses the following structure for calculations:

.. image:: ./_static/calculation_functions.png

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

.. code-block:: python

    FairException: Not ready for calculation. See statuses: 
    Risk                                  Required
    Loss Event Frequency                  Supplied
    Threat Event Frequency            Not Required
    Contact Frequency                 Not Required
    Probability of Action             Not Required
    Vulnerability                     Not Required
    Control Strength                  Not Required
    Threat Capability                 Not Required
    Loss Magnitude                        Required
    Primary Loss                          Required
    Secondary Loss                        Required
    Secondary Loss Event Frequency        Required
    Secondary Loss Event Magnitude        Required

The reason for this is readily apparent when looking at the calculation
tree:

.. image:: ./_static/incomplete_example.png

As you can see, you supplied "Loss Event Frequency". That means you do not
need to calculate "Loss Event Frequency"--and you also don't have to
deal with anything underneath it because it's all superfluous. That said,
you cannot calculate Risk because the whole right side of the FAIR
calculation hasn't been supplied.

If you were create a new model with "Loss Magnitude" and "Loss Event
Frequency" you'd cover both branches of the FAIR model and would receive
no error. Notice that you did not have to supply information for everything
in the error above. pyfair lists them all as required because it has no
idea what you're going to put in next (and so it doesn't know whether it
will be high on the tree or low on the tree).

Why do my simulation results change from run to run?
----------------------------------------------------

Monte Carlo simulations are an attempt to harness large numbers of random
simulations to model complex outcomes. pyfair seeds its random number
generation with a so-called "random seed". This makes the outcome
deterministic, even though it appears random. As a consequence, we can run
a pyfair simulation today and a simulation tomorrow, and they will come out
the same if the parameters are the same.

By default, the random seed is 42. If you're reading this, you've probably
changed the random seed.
