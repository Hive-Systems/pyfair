from distutils.core import setup

setup(
    name='pyfair',
    version='0.1-alpha.8',
    description='FAIR Monte Carlo creator',
    long_description="""
        Factor Analysis of Information Risk (FAIR) model written in Python.

        This package endeavors to create a simple API for automating the
        creation of FAIR Monte Carlo risk simulations.

        This is based in large part on:
            * the Technical Standard published by the Open Group; and,
            * Measuring and Managing Information Risk.
    """,
    author='Theo Naunheim',
    author_email='theonaunheim@gmail.com',
    packages=[
        'pyfair',
        'pyfair.model',
        'pyfair.report',
        'pyfair.utility',
    ],
    license='MIT',
    url='https://github.com/theonaunheim/pyfair',
    keywords=[
        'FAIR',
        'risk'
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
    ],
    requires=[
        'pandas',
        'numpy',
        'scipy',
        'matplotlib',
        'xlrd',
    ],
    package_dir={'pyfair': './pyfair'},
    package_data={'pyfair': ['./static/*']},
)
