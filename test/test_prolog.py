
try:
	import readline
except ImportError:
	pass
	
from pyswip.util import PrologRunner

def main():
	prolog = PrologRunner()
	
	while 1:
		try:
			cmd = raw_input(">>> ")
		except EOFError:
			print
			break
			
		result = prolog.query(cmd)
		if not result:
			print "No"
		elif not result[0]:
			print "Yes"
		else:
			print result
## 			for r in result:
####				print "\n".join(["%s=%s" % kv for kv in r.iteritems()])
## 				print r
## 				print "-"*10
				

if __name__ == "__main__":
	main()
