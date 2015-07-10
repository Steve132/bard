import os,os.path
import json
import collections.MutableMapping

class metadata_db(collections.MutableMapping):
	def __init__(self,root,metafolder='.meta'):
		self.leaves={}
		self.branches={}
		self.rootpath=root
		self.absrootpath=os.path.abspath(root)
		self.metapath=os.path.join(root,metafolder)
		if(os.path.exists(self.metapath)):
			for mdfn in os.listdir(self.metapath):
				if(fn.
		for fn in os.listdir():
			self.leaves=
	def __getitem__(self,key):
		pass
	def __setitem__(self,key,value):
		pass
	def __delitem__(self,key):
		pass
	def __iter__(self);
		pass
	def __len__(self):
		pass
		
	def __retrieve_key(self,keyfile):
		return json.load(open(keyfile,'r'))
	def __setkey(self,keyfile,value):
		json.dump(value,open(keyfile,'w'))
	def __delkey(self,keyfile,value):
		os.remove(keyfile)
