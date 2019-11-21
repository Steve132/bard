import sys
import base64
import json
from urllib.parse import quote,unquote
import threading
from collections import MutableMapping

class ReplayDB(MutableMapping):
	def _decode(self,c):
		s=unquote(c)
		#s=base64.standard_b64decode(s)
		return json.loads(s)
	def _encode(self,o):
		s=json.dumps(o)
		c=quote(s)
		#c=base64.standard_b64encode(s)
		return c
	def _writeop(self,op,key,value):
		self.replayfileobj.write("%s %s %s\n" % (op,self._encode(key),self._encode(value)))

	def __init__(self,replayfile,compress_history=True):		
		self.rdb={}
		self.lock=threading.Lock()
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
						elif(op=='='):
							self.rdb[k]=v
						elif(op=="+"):
							self.setdefault(k,set()).add(v)
						elif(op=="-"):
							self.setdefault(k,set()).remove(v)
					except Exception as e1:
						print("error unpacking in %s:%r.  (%r,%r)" % (replayfile,e1,ke,ve))
		except Exception as e:
			pass#print("couldn't open %s:%r" % (replayfile,e))

		if(compress_history):
			self.replayfileobj=open(replayfile,'w')
			for k,v in self.rdb.items():
				self._writeop("=",k,v)
		else:
			self.replayfileobj=open(replayfile,'w+')
		
	
	def __getitem__(self,key):
		with self.lock:
			return self.rdb[key]

	def __setitem__(self,key,value):
		with self.lock:
			ov=self.rdb.get(key,None)
			if(not (ov == value)):
				self._writeop("=",key,value)
				self.rdb[key]=value

	def __delitem__(self,key):
		with self.lock:
			self._writeop("d",key,None)
			del self.rdb[key]

	def __contains__(self,key):
		return key in self.rdb

	def keys(self):
		return self.rdb.keys()

	def __iter__(self):
		return self.rdb.__iter__()

	def __len__(self):
		return len(self.rdb)
