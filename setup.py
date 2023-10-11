from setuptools import setup

setup(
    name="pyfair",
    version="0.1-alpha.12",
    description="Open FAIR Monte Carlo creator",
    long_description="""
        Factor Analysis of Information Risk (Open FAIR) model in Python.

        This package endeavors to create a simple API for automating the
        creation of FAIR Monte Carlo risk simulations.

        This is based on the terms found in:

        1. Open FAIR™ RISK TAXONOMY (O-RT); and,
        2. Open FAIR™ RISK ANALYSIS (O-RA).

        "Open FAIR" is a trademark of the Open Group.

    """,
    author="Theo Naunheim",
    author_email="theonaunheim@gmail.com",
    packages=[
        "pyfair",
        "pyfair.model",
        "pyfair.report",
        "pyfair.utility",
    ],
    license="MIT",
    url="https://github.com/theonaunheim/pyfair",
    keywords=["FAIR", "risk"],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "License :: OSI Approved :: MIT License",
    ],
    requires=[
        "pandas",
        "numpy",
        "scipy",
        "matplotlib",
        "xlrd",
    ],
    package_dir={"pyfair": "./pyfair"},
    package_data={"pyfair": ["./static/*"]},
)
