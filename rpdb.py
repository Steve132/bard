import json
import base64
import collections

	

def mergedict(dic,targ):
	if(isinstance(dic,collections.Mapping) and isinstance(targ,collections.Mapping)):
		if(not isinstance(dic,collections.MutableMapping)):
			dic=dict(dic)
		for k,v in dic.items():
			if(k in targ[v
			dic[k]=mergedict(v,targ[k])
	else:		#if one is a dict and the other is not, throw an error.
		#if(both are not strings and iterable, join the lists)
		#if just one is not a string and not iterable, join the other one to the list.
		#if neither are iterable, make a list and combine them.
		#if one is none, return the other.  
		#if both are none, return none
		
class rpdb(object):

	@classmethod
	def _decode(b64):
		return json.loads(base64.urlsafe_b64decode(b64))
	@classmethod(dic):
		return base64.urlsafe_b64decode(json.dumps(dic))

	def __init__(self,writefile,readfile=None):
		self.db={}
		if(isinstance(writefile,basestring)):
			self.fileobject=open(writefile,'a+')
		else
			self.fileobject=writefile

		for l in self.fileobject:
			self._readline(l)
			
		if(readfile):
			if(isinstance(readfile,basestr):
				rfile=open(readfile,'r')
			else:
				rfile=readfile
		for l in rfile:
			self._readline(l)
	
	
	def _recurse(self,path,ref=self.db,create=True):
		for p in path:
			if(create):
				ref=ref.setdefault(p,{})
			else:
				ref=ref[p]
			
		
	def _readline(self,line):
		elements=line.split()
		cmd=elements[0].lower()
		path=elements[1:-1]
		data=elements[-1]
		if(cmd in ["set","s","="]):
			loc=self._recurse(path[:-1])
			loc[path[-1]]=data
			if(not data):
				del loc[path[-1]]
		elif(cmd in ["merge","m","+"]):
			loc=self._recurse(path[:-1])
			loc[path[-1]]=mergedict(loc[path-1],data)
		else:
			raise Exception("Unrecognized command '%s')
		
			
			
		
		
