Calculation Details
===================

The nodes can be described as follows:

#. **Risk ("R")**

    Description: a vector of currency values/elements, which represent the
    ultimate loss for a given time period

    Restrictions: all elements must be positive

    Derivation: multiply the Loss Event Frequency vector by the Loss
    Magnitude vector

    .. math::

        \begin{bmatrix}
            \text{R}_{1} \\
            \text{R}_{2} \\
            \vdots \\
            \text{R}_{m}
        \end{bmatrix}
        =
        \begin{bmatrix}
            \text{LEF}_{1} \\
            \text{LEF}_{2} \\
            \vdots \\
            \text{LEF}_{m}
        \end{bmatrix}
        \times
        \begin{bmatrix}
            \text{LM}_{1} \\
            \text{LM}_{2} \\
            \vdots \\
            \text{LM}_{m}
        \end{bmatrix}

    
    Example: For a given year the following dollar amounts:

    .. math::

        \begin{bmatrix}
            \text{\$1,500,000} \\
            \text{\$0} \\
            \vdots \\
            \text{\$527,000} \\
        \end{bmatrix}

#. **Loss Event Frequency ("LEF")**

    Description: a vector of elements which represent the number of times a 
    particular loss occurs during a given time frame (generally one year)

    Restrictions: all elements must be positive

    Derivation: supplied directly, or multiply the Threat Event Frequency 
    vector by the Vulnerability vector

    .. math::

        \begin{bmatrix}
            \text{LEF}_{1} \\
            \text{LEF}_{2} \\
            \vdots \\
            \text{LEF}_{m}
        \end{bmatrix}
        =
        \begin{bmatrix}
            \text{TEF}_{1} \\
            \text{TEF}_{2} \\
            \vdots \\
            \text{TEF}_{m}
        \end{bmatrix}
        \times
        \begin{bmatrix}
            \text{V}_{1} \\
            \text{V}_{2} \\
            \vdots \\
            \text{V}_{m}
        \end{bmatrix}

    Example: Count of breaches resulting in data loss (for given year):

    .. math::

        \begin{bmatrix}
            \text{5} \\
            \text{1} \\
            \vdots \\
            \text{10} \\
        \end{bmatrix}

#. **Threat Event Frequency ("TEF")**

    Description: a vector of elements representing the number of times a 
    particular threat occurs, whether or not it results in a loss

    Restrictions: all elements must be positive

    Derivation: supplied directly, or multiply the Contact Frequency vector
    and the Probability of Action vector

    .. math::

        \begin{bmatrix}
            \text{TEF}_{1} \\
            \text{TEF}_{2} \\
            \vdots \\
            \text{TEF}_{m}
        \end{bmatrix}
        =
        \begin{bmatrix}
            \text{C}_{1} \\
            \text{C}_{2} \\
            \vdots \\
            \text{C}_{m}
        \end{bmatrix}
        \times
        \begin{bmatrix}
            \text{A}_{1} \\
            \text{A}_{2} \\
            \vdots \\
            \text{A}_{m}
        \end{bmatrix}

    Example: Count of cross-site scripting attempts in a given month

    .. math::

        \begin{bmatrix}
           \text{9,400} \\
           \text{8,010} \\
           \vdots \\
           \text{8,200} \\
        \end{bmatrix}

#. **Vulnerability ("V")**

    Description: a vector of elements with each value representing the
    probability that a potential threat actually results in a loss

    Restrictions: all elements must be from 0.0 to 1.0

    Derivation: supplied directly, or via the following operation:
    
    .. math::

        \bar{V}
        \;
        \text{Where}
        \;
        V_{i}
        =
        \begin{cases}
            1, & \text{if} \; \text{TC}_{i} \; \geq \text{CS}_{i}\\
            0, & \text{if} \; \text{TC}_{i} \; \lt \text{CS}_{i}\\
        \end{cases}

    Or in other words:

    For each simulation, see if Threat Capability is greater than Control
    Strength. If TC is greater than CS, that simulation's value is 1.
    Otherwise it is zero. After this vector of zeros and ones is created,
    take the average of that vector. This number will be between zero and 
    one, and will represent the percentage of the population in which TC 
    was greater than CS (and by extension, which percentage of the
    population we can expect to be vulnerable).

    For example, say we have TCs:

    .. math::

        \begin{bmatrix}
           \text{V}_{1} \\
           \text{V}_{2} \\
           \vdots \\
           \text{V}_{m}
        \end{bmatrix}
        =
        \begin{bmatrix}
           \text{TC}_{1} \\
           \text{TC}_{2} \\
           \vdots \\
           \text{TC}_{m}
        \end{bmatrix}
        \times
        \begin{bmatrix}
           \text{CS}_{1} \\
           \text{CS}_{2} \\
           \vdots \\
           \text{CS}_{m}
        \end{bmatrix}

    For item one, TC is .60 and CS is .55. and consequently our resulting
    first item will be 1 (because it's vulnerable) For item two, TC is .70
    and CS is .65, and consequently our resulting second item will be 1
    (because it's vulnerable). For item 3, our TC is .10 and our CS is .75,
    and consequently our resulting third item will be zero (because it's
    not vulnerable. The resulting matrix will be made of 0.66 values, 
    which in turn means our Vulnerability vector will be a lot like a
    scalar value.

    Example: the percentage of phishing attempts that result in loss:

    .. math::

        \begin{bmatrix}
           0.76 \\
           0.89 \\
           \vdots \\
           0.72 \\
        \end{bmatrix}

#. **Contact Frequency ("C")**

    Description: a vector with elements representing the number of threat 
    actor contacts that could potentially  yield a threat within a given 
    timeframe

    Restrictions: all elements must be a positive number

    Derivation: None (this must be supplied, not calculated)

    Example: For a given year, the number of ports scans:

   .. math::

        \begin{bmatrix}
           12,000 \\
           10,150 \\
           \vdots \\
           13,000 \\
        \end{bmatrix}

#. **Probability of Action ("A")**

    Description: a vector with elements representing the probability that 
    a threat actor will proceed after coming into contact with an
    organization 

    Restrictions: all elements must be number from 0.0 to 1.0

    Derivation: None (this must be supplied, not calculated)

    Example: the percent of times that an actor will proceed to attack an
    open SSH port:

    .. math::

        \begin{bmatrix}
           0.45 \\
           0.49 \\
           \vdots \\
           0.46 \\
        \end{bmatrix} 

#. **Threat Capability ("TC")**

    Description: a vector of unitless elements that describe the relative 
    level of expertise and resources of a threat actor (relative to a
    Control Strength)

    Restrictions: all elements must be number from 0.0 to 1.0

    Derivation: None (this must be supplied, not calculated)

    Example: the relative strengths of threat actors:

   .. math::

        \begin{bmatrix}
           0.99 \\
           0.95 \\
           \vdots \\
           0.80 \\
        \end{bmatrix}

#. **Control Strength ("CS")**

    Description: a vector of unitless elements that describe the relative 
    strength of a given control (relative to the Threat Capability of a 
    given actor)

    Restrictions: must be a number from 0.0 to 1.0

    Derivation: None (this must be supplied, not calculated)

    Example: the relative strength of a particular control:

   .. math::

        \begin{bmatrix}
           0.80 \\
           0.81 \\
           \vdots \\
           0.82 \\
        \end{bmatrix}    

#. **Loss Magnitude ("LM")**

    Description: a vector of currency values describing the total loss for
    a given Loss Event

    Restrictions: all elements must be positive

    Derivation: supplied directly, or the sum of the Primary Loss vector 
    and Secondary Loss vector

    .. math::

        \begin{bmatrix}
            \text{LM}_{1} \\
            \text{LM}_{2} \\
            \vdots \\
            \text{LM}_{m}
        \end{bmatrix}
        =
        \begin{bmatrix}
            \text{PL}_{1} \\
            \text{PL}_{2} \\
            \vdots \\
            \text{PL}_{m}
        \end{bmatrix}
        +
        \begin{bmatrix}
            \text{SL}_{1} \\
            \text{SL}_{2} \\
            \vdots \\
            \text{SL}_{m}
        \end{bmatrix}

    Example: the monetary value for a successful breach:

    .. math::

        \begin{bmatrix}
            $1,000,110 \\
            $2,001,968 \\
            \vdots \\
            $1,523,100
        \end{bmatrix}

#. **Primary Loss ("PL")**

    Description: the amount of the loss directly attributable to the threat

    Restrictions: must be a positive number

    Derivation: None (this must be supplied, not calculated)

    Example: 25,000,000 (dollars in funds stolen)

#. **Secondary Loss ("SL")**

    Description: the amount of loss incurred as a secondary consequence of
    the loss

    Restrictions: must be a positive number

    Derivation: supplied directly, or the aggregate sum of the Secondary
    Loss Event Frequency and Secondary Loss Event Magnitude vectors
    multiplied together

    Example: 5,000,000 (dollars worth of data research/cleanup post-breach)

#. **Secondary Loss Event Frequency ("SLEF")**

    Description: the probability that a given secondary loss could occur

    Restrictions: must be a vector of numbers from 0.0 to 1.0

    Derivation: None (this must be supplied, not calculated)

    Example: [.25, .80, 1.0] (probabilities of loss for 3 loss types)

#. **Secondary Loss Event Magnitude ("SLEM")**

    Description: the amount of the secondary loss that could occur

    Restrictions: must be a vector of positive numbers

    Derivation: None (this must be supplied, not calculated)

    Example: [100, 900, 200] (magnitude of loss for 3 loss types)

.. note::

    As implemented by pyfair, Secondary Loss is an aggregate field that is
    create using a vectors of values. This is an exception to the single
    value per simulation condition we discussed earlier.
