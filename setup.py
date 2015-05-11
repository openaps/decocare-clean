#!/usr/bin/python

from setuptools import setup, find_packages

import decocare
def readme():
    with open("README.markdown") as f:
        return f.read()

setup(name='decocare',
    version='0.0.11', # http://semver.org/
    description='Audit, inspect, and command MM insulin pumps.',
    long_description=readme(),
    author="Ben West",
    author_email="bewest+insulaudit@gmail.com",
    url="https://github.com/bewest/decoding-carelink",
    #namespace_packages = ['insulaudit'],
    packages=find_packages( ),
    install_requires = [
      'pyserial', 'python-dateutil', 'argcomplete'
    ],
    scripts = [
      'bin/mm-press-key.py',
      'bin/mm-send-comm.py',
      'bin/mm-set-suspend.py',
      'bin/mm-temp-basals.py',
      'bin/mm-decode-history-page.py',
      'bin/mm-latest.py',
      'bin/mm-bolus.py',
      'bin/mm-set-rtc.py',
      'bin/mm-pretty-csv',
    ],
    classifiers = [
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'Programming Language :: Python',
        'Topic :: Scientific/Engineering',
        'Topic :: Software Development :: Libraries'
    ],
    include_package_data=True,
    zip_safe=False
)

#####
# EOF
