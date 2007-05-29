
# PySWIP setup script

import sys
import os
import os.path
from distutils.core import setup

setup(name="pyswip",
		version="0.1.2",
		url="http://code.google.com/p/pyswip/",
		download_url="http://code.google.com/p/pyswip/downloads/list",
		author="Yuce Tekol",
		author_email="yucetekol@gmail.com",
		description="PySWIP enables querying SWI-Prolog in your Python programs.",
		long_description="""PySWIP is a GPL'd Python - SWI-Prolog bridge which enables querying SWI-Prolog in your Python programs.
		
		PySWIP includes both an (incomplete) SWI-Prolog foreign language interface and a utity class that makes it easy querying SWI-Python.
		
		Example:
			>>> from pyswip.util import Prolog
			>>> prolog = Prolog()
			>>> prolog.assertz("father(michael,john)")
			[{}]
			>>> prolog.assertz("father(michael,gina)")
			[{}]
			>>> list(prolog.query("father(michael,X)"))
			[{'X': 'john'}, {'X': 'gina'}]
			>>> for soln in prolog.query("father(X,Y)"):
			...     print soln["X"], "is the father of", soln["Y"]
			...
			michael is the father of john
			michael is the father of gina
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
