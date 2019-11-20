import hashlib
import topo

def _nullamd(k,v):
	return None

class PathRegistry(object):
	def __init__(self):
		self.depends={}
		self.funcs={}
		self.topo_rank=None
	def register(self,tag,func,depends=[]):
		if(tag in self.funcs):
			raise Exception("tag already is registred")
		self.funcs[tag]=func
		self.depends[tag]=set(depends)
		self.topo_rank=None

	def _ensuretopo(self):
		if(self.topo_rank is None):
			topolist=topo.topo(self.depends)
			self.topo_rank={v:i for i,v in enumerate(topolist)}

	def expand_paths(self,paths):
		self._ensuretopo()
		outdeps=set()
		def trace_deps(n):
			if(n in outdeps):
				return
			for d in self.depends.get(n,[]):
				trace_deps(d)
			outdeps.add(n)
		for p in paths:
			trace_deps(p)
		return sorted(outdeps,key=lambda n: self.topo_rank[n])
		
	def compute_path(self,key,value,path,*args,**kwargs):
		p=path
		if(p not in value):
			pfunc=self.funcs.get(p,_nullamd)
			v=pfunc(key,value,*args,**kwargs)
			value[p]=v

		return value[p]


	def get_default_paths_from_type(key):
		return ['/any/contenthash']

#path registry has the pre-topological sorted indices that it uses as a key 
#def expand_paths(key,value,paths):
#	if(paths == None):
#		paths=get_default_paths_from_type(key)


registry=PathRegistry()

def pathfunc(path,depends=[]):
	def wrapper(f):
		global registry
		registry.register(path,f,depends)
		return f
	return wrapper

