import os
from setuptools import setup, find_packages

with open(os.path.join(os.path.dirname(__file__), 'README.rst')) as readme:
    README = readme.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='django-cvmfs-browser',
    version='0.2.0',
    include_package_data=True,
    license='(c) 2014 CERN - BSD License',
    description='A simple Django application to interactively \"mount\" '
                'a set of CernVM-FS repositories in the browser.',
    long_description=README,
    url='http://cernvm.cern.ch/portal/startcvmfs/',
    author='Jose Molina Colmenero',
    author_email='jose.molina@cern.ch',
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 2.7.10',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content'
    ],
    packages=find_packages(),
    install_requires=[
        'python-cvmfsutils >= 0.1.0',
        'Django >= 1.8',
    ]
)
