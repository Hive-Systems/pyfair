Generally
=========

Overview
--------

If you are already familiar with FAIR, please skip to `Getting Started
With pyfair`_.

`Factor Analysis for Information Risk (FAIR)
<https://en.wikipedia.org/wiki/Factor_analysis_of_information_risk>`_
is a methodology for analyzing cybersecurity risk. In a general sense, it
works by breaking risk into its individual components. These components can
then be measured or estimated numerically, allowing for a quantitative 
calculation of risk as a whole.

.. note::

    "Risk" in FAIR is defined as the total dollar amount of expected loss
    for a given time frame. If you come from a traditional risk management
    background, you likely refer to this as the more commonly accepted term
    "Loss Exposure". This documentation will use the FAIR nomenclature.

The actual calculation for Risk often takes the form of a `Monte Carlo
method <https://en.wikipedia.org/wiki/Monte_Carlo_method>`_. This Monte
Carlo method supplies random inputs for our model. The model then
transforms the inputs in accordance with FAIR calculation rules, and 
provides outputs. The outputs can then be analyzed to determine what the 
potential range of Risk values are. pyfair's purpose is to simplify and 
automate these Monte Carlo methods.

A Quick Monte Carlo Example
---------------------------

Generally speaking, Monte Carlo experiments are a class of techniques that 
solve problems using random sampling. Within the context of FAIR they are
used to estimate loss by performing calculations on random inputs. This is
a brief demonstration of how you can use a Monte Carlo method without
knowing anything about FAIR.

Say we know the average height and average weight a certain population
looks like, but we don't know what the average `Body Mass Index (BMI)
<https://en.wikipedia.org/wiki/Body_mass_index>`_ looks like:

.. image:: ./_static/before_monte_carlo_bmi.png

We can use the weight and height distributions from the data we do know to 
randomly generate 3 height samples and 3 weights samples.

+--------+-------------+-------------+
| Sample | Weight (kg) | Height (cm) |
+========+=============+=============+
| 1      | 41          | 107         |
+--------+-------------+-------------+
| 2      | 52          | 139         |
+--------+-------------+-------------+
| 3      | 85          | 131         |
+--------+-------------+-------------+ 

We take these generated samples, and for each For each of these samples, 
we calculate the samples' BMI using the following formula:

.. math::

    \text{BMI} = \frac
            {\text{Weight}_{kg}}
            {(\text{Height}_{cm} \times .01) ^2}

+--------+-------------+-------------+-----+
| Sample | Weight (kg) | Height (cm) | BMI |
+========+=============+=============+=====+
| 1      | 41          | 107         | 36  |
+--------+-------------+-------------+-----+
| 2      | 52          | 139         | 27  |
+--------+-------------+-------------+-----+
| 3      | 85          | 131         | 50  |
+--------+-------------+-------------+-----+ 

Once we have these BMIs, we can calculate the mean and spread of these
BMIs. With 3 samples, this doesn't give us a lot of data, but if we were to 
run 10,000 or so samples, we would get a distribution like this:

.. image:: ./_static/after_monte_carlo_bmi.png

Most Monte Carlo simulations follow a similar process. We generate random
inputs in accordance with a particular distribution, and we then run these
inputs through complex or arbitrary formulae we cannot analyze otherwise. 
The output can then be used to infer what an expected output population
looks like.

Nodes
-----

Risk in FAIR (and by extension Risk in our Monte Carlo simulation) is
broken down into a series of what pyfair calls "nodes" for calculation.
The user supplies two or more of these nodes to generate random data, which
in turn will allow us to calculate the mean, max, min, and standard
deviation of the Risk and other nodes.

.. note::

    While we refer to the data in these nodes, it is important to remember
    that we are talking about a single simulation within the Monte Carlo
    model. For example, if we have 1,000 simulations, we will have a 
    `vector <https://en.wikipedia.org/wiki/Row_and_column_vectors>`_ of
    1,000 elements. This will become more clear in the  `FAIR by Example`_ 
    section.

The nodes are as follows:

.. image:: ./_static/calculation_functions.png

One of the benefits of FAIR is the flexibility that comes with being able
to pick and choose the data you supply. If you want to supply Loss Event
Frequency, and Loss Magnitude, you can do that.

.. image:: ./_static/lef_and_lm_example.png

If you want to supply Threat Event Frequency, Threat Capability, Control
Strength, Primary Loss, and Secondary Loss, you can do that to.

.. image:: ./_static/tef_tc_cs_pl_and_sl_example.png

As you can likely see from the above examples, you only need to supply the
bare minimum to complete the calculation. The general rule with pyfair is
that to properly calculate any node, the node's child nodes need to either
be calculable or supplied.

FAIR by Example
---------------

This is a quick example of how one might conduct a FAIR calculation by
hand. You will likely never need to do this, but it does provide a concrete
example of how everything works.

For the purposes of this demonstration, we will keep it simple. We will run
a Monte Carlo model composed of three separate simulations and using three
inputs. These inputs will be Threat Event Frqeuency (TEF), Vulnerability
(V), and Loss Magnitude (LM). We will use this simulation to estimate the 
Risk associated with allowing all ports to remain open.

The general approach will be as follows:

.. image:: ./_static/fair_by_example_with_numbers.png

* Step 1: Generate random values to supply TEF, V, and LM
* Step 2: Multiply your TEF and V values to calculate LEF
* Step 3: Multiply your LEF and LM to calculate Risk
* Step 4: Analyze your Risk outputs

Step 1: Generate Our Random Inputs
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

We start by generating our data. We will generate 3 values for Threat Event
Frequency (TEF), 3 values for Vulnerability (V), and 3 values for Loss
Magnitude (LM). Most often in FAIR you will see BetaPert distributed random
variates. For the sake of simplicity this example will use normally
distributed random variates.

First we will estimate TEF. Recall that TEF is the number of threats that
occur whether or not it result in a loss (which is represented by a
positive number). Here we estimate that if leave these ports open, we will 
see around 50,000 attempted intrusions with a standard deviation of 10,000
events. We will then generate three normally distributed random numbers 
from a curve with a mean of 50,000 and a standard deviation of 10,000.

+------------+--------------------+
| Mean       | Standard Deviation |
+============+====================+
| 50,000     | 10,000             |
+------------+--------------------+

**Generates random TEF values**

+------------+--------+
| Simulation | TEF    |
+============+========+
| 1          | 53,091 |
+------------+--------+
| 2          | 38,759 |
+------------+--------+
| 3          | 44,665 |
+------------+--------+ 

Second we will estimate our Vulnerability. Recall that V is the probability
of whether a loss occurs.

+------------+--------------------+
| Mean       | Standard Deviation |
+============+====================+
| .67        | .01                |
+------------+--------------------+

**Generates random V values**

+------------+-----+
| Simulation | V   |
+============+=====+
| 1          | .66 |
+------------+-----+
| 2          | .67 |
+------------+-----+
| 3          | .68 |
+------------+-----+ 

Third we will estimate our loss magnitude. Recall that LM is the amount of
loss for each Loss Event (represented by a positive number). We estimate 
that on average each loss will result in an average of a $100 loss, with a
standard deviation of $50. We then generate three normally distributed
random numbers from a curve with a mean of 100 and a standard deviation
of 50.

+------+--------------------+
| Mean | Standard Deviation |
+======+====================+
| 100  | 50                 |
+------+--------------------+

**Generates random LM values**

+------------+-----+
| Simulation | LM  |
+============+=====+
| 1          | 198 |
+------------+-----+
| 2          | 150 |
+------------+-----+
| 3          | 86  |
+------------+-----+ 

Step 2: Calculate LEF Using TDF and V
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

As you can likely see, we can use our 3 TEFs and 3 Vs and multiply them
together element-by-element. This will give us 3 LEF values. 

+------------+--------+-----+-------------------+
| Simulation | TEF    | V   | LEF (TEF times V) |
+============+========+=====+===================+
| 1          | 53,091 | .66 | 35,040            |
+------------+--------+-----+-------------------+
| 2          | 38,759 | .67 | 25,968            |
+------------+--------+-----+-------------------+
| 3          | 44,665 | .68 | 30,372            |
+------------+--------+-----+-------------------+

This follows with what we known know about Loss Event Frequency. It is the
amount of loss that actually occurs. We have a three potential losses, and
two of those losses actually occur. The others do not occur, so the amount
of loss is zero.

Step 3: Calculate Our R Using LEF and LM
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Now that we have an LEF and an LM, we can calculate our final Risk, R. R is
calculated by taking the total number of loss events and multiplying them
by the amount lost for each event.

+------------+--------+-----+------------------+
| Simulation | LEF    | LM  | R (LEF times LM) |
+============+========+=====+==================+
| 1          | 35,040 | 198 | 6,937,920        |
+------------+--------+-----+------------------+
| 2          | 25,968 | 150 | 3,895,200        |
+------------+--------+-----+------------------+
| 3          | 30,372 | 86  | 2,612,009        |
+------------+--------+-----+------------------+

Step 4: Analyze Our Risk Outputs
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

By using our random inputs and putting them through our Monte Carlo model
we were able to calculate Risk for three simulations. The resulting Risk
from these simulations is $10,512,018, $0, and $4,841,190. Now that we have
conducted our simulation we've learned that with our estimates we can
expect our Risk to have the following attributes:

+------------+-------------------------+
| Risk Mean  | Risk Standard Deviation |
+============+=========================+
| $4,481,709 | $2,221,794              |
+------------+-------------------------+

pyfair, as you will see later on, makes this considerably easier. You
should be able to achieve similar results with 5 to 10 lines of code.

.. code-block:: python

    from pyfair import FairModel


    # Create our model and calculate (don't worry about understanding yet)
    model = FairModel(name='Sample')
    model.input_data('Threat Event Frequency', mean=50_000, stdev=10_000)
    model.input_data('Vulerability', mean=.66, stdev=.01)
    model.input_data('Loss Magnitude', mean=100, stdev=50)
    model.calculate_all()

.. image:: ./_static/calculation_example.png
