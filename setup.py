import os
from setuptools import setup, find_packages

with open(os.path.join(os.path.dirname(__file__), 'README.rst')) as readme:
    README = readme.read()

setup(
    name='cvmfs-browser',
    version='0.2.0',
    packages=find_packages(),
    include_package_data=True,
    license='(c) 2014 CERN - BSD License',
    description='A simple Django application to interactively \"mount\" '
                'a set of CernVM-FS repositories in the browser.',
    long_description=README,
    zip_safe=False,
    url='https://github.com/cvmfs/cvmfs-browser',
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
    package_data={'cvmfs_browser': ['static/**/**/**/**/**',
                                    'static/js/*.js',
                                    'static/css/*.css',
                                    'static/img/custom/*',
                                    'templates/cloud_browser/admin/*.html',
                                    'templates/cloud_browser/*.html']},
    data_files=[('', ['README.rst', 'INSTALL', 'COPYING'],)],
    install_requires=[
        'cvmfsutils >= 0.3.0',
        'Django == 1.8',
        'python-magic',
        'httpagentparser >= 1.7.8',
    ],
)
