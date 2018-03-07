from os import path

from setuptools import setup, find_packages

version = None
exec(open('augurycli/version.py').read())

with open(path.join(path.abspath(path.dirname(__file__)), 'README.rst')) as f:
    long_description = f.read()

setup(name='augurycli',
      version=version,
      description='CLI utility for running and retrieving results from Augury',
      long_description=long_description,
      author='Jared Lewis',
      author_email='jared@jared.kiwi.nz',
      license='MIT',
      keywords='wrf cli cloud science forecast',
      classifiers=[
          'Development Status :: 4 - Beta',
          'Intended Audience :: Science/Research',
          'Intended Audience :: System Administrators',
          'License :: OSI Approved :: MIT License',
          'Programming Language :: Python :: 2',
          'Programming Language :: Python :: 3',
          'Topic :: Scientific/Engineering :: Atmospheric Science'
      ],
      install_requires=[
          'requests',
          'six'
      ],
      packages=find_packages(exclude='tests'),
      entry_points={
          'console_scripts':
              ['augury = augurycli.cli:main']
      },
      zip_safe=False)
