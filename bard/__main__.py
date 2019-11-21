import sys
import bard

if __name__=="__main__":
	bdb=bard.BardDB(".barddb")
	bdb.sync(sys.stdin)
