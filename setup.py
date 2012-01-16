from setuptools import setup, find_packages
import os

version = '1.0'

setup(name='oerpub.rhaptoslabs.sword2cnx',
      version=version,
      description="A library that implements the SWORD2 API specification to communicate with Connexions (cnx.org), a Rhaptos instance.",
      long_description=open("README.rst").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from
      # http://pypi.python.org/pypi?:action=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        ],
      keywords='',
      author='Carl Scheffler',
      author_email='carl.scheffler@gmail.com',
      url='https://github.com/oerpub/oerpub.rhaptoslabs.sword2cnx',
      license='LGPLv3',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['oerpub', 'oerpub.rhaptoslabs'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
          'sword2',
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
