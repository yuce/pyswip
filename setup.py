
# PySWIP setup script

import sys
import os
import os.path
from distutils.core import setup

setup(name="pyswip",
		version="0.1.0",
		url="http://code.google.com/p/pyswip/",
		download_url="http://code.google.com/p/pyswip/downloads/list",
		author="Yuce Tekol",
		author_email="yucetekol@gmail.com",
		description="PySWIP enables querying SWI-Prolog in your Python programs.",
		long_description="""PySWIP is a GPL'd Python - SWI-Prolog bridge enabling to query SWI-Prolog in your Python programs.
		
		Example:
			>>> prolog.query("assertz(father(michael,john)).")
			[{}]
			>>> prolog.query("assertz(father(michael,gina)).")
			[{}]
			>>> prolog.query("father(michael,X).")
			[{'X': 'john'}, {'X': 'gina'}]
		""",
		license="GPL",
		packages=["pyswip"],
		classifiers=[
			'Development Status :: 3 - Alpha',
			'Intended Audience :: Developers',
			'Intended Audience :: Science/Research',
			'License :: OSI Approved :: GNU General Public License (GPL)',
			'Operating System :: OS Independent',
			'Programming Language :: Python',
			'Topic :: Scientific/Engineering :: Artificial Intelligence',
			'Topic :: Software Development :: Libraries :: Python Modules'
			],
		)
