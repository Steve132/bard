import sys
import base64
import json
import urllib
from collections import MutableMapping

class ReplayDB(MutableMapping):
	def _decode(self,c):
		s=urllib.unquote(c)
		#s=base64.standard_b64decode(s)
		return json.loads(s)
	def _encode(self,o):
		s=json.dumps(o)
		c=urllib.quote(s)
		#c=base64.standard_b64encode(s)
		return c

	def _writeset(self,key,value):
		self.replayfileobj.write("s %s %s\n" % (self._encode(key),self._encode(value)))
	def _writedel(self,key):
		self.replayfileobj.write("d %s NONE\n" % (self._encode(key)))

	def __init__(self,replayfile):		
		self.rdb={}
		
		try:
			with open(replayfile,'r') as trpfob:
				for entry in trpfob:
					try:
						op,ke,ve=entry.split()
				
						k=self._decode(ke)
						v=self._decode(ve)
						k=tuple(k)
				
						if(op=='d'):
							del self.rdb[k]
						elif(op=='s'):
							self.rdb[k]=v
					except Exception as e1:
						print("error unpacking in %s:%r.  (%r,%r)" % (replayfile,e1,ke,ve))
		except Exception as e:
			print("couldn't open %s:%r" % (replayfile,e))

		self.replayfileobj=open(replayfile,'w+')
		for k,v in self.rdb.items():
			#print("WRITEBACK "+str(k)+':'+str(v))
			self._writeset(k,v)
	
	def __getitem__(self,key):
		return self.rdb[key]

	def __setitem__(self,key,value):
		ov=self.rdb.get(key,None)
		if(not (ov == value)):
			self._writeset(key,value)
		self.rdb[key]=value

	def __delitem__(self,key):
		self._writedel(key)
		del self.rdb[key]

	def __contains__(self,key):
		return key in self.rdb

	def keys(self):
		return self.rdb.keys()

	def __iter__(self):
		return self.rdb.__iter__()

	def __len__(self):
		return len(self.rdb)
