from distutils.core import setup

setup(
    name='pyfair',
    version='0.1.0',
    description='Factor Analysis of Information Security RIsk (FAIR) Monte Carlo creator',
    author='Theo Naunheim',
    author_email='theonaunheim@gmail.com',
    packages=[
        'pyfair', 
        'pyfair.model'
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