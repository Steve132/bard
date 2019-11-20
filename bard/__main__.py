import path_identifier 
import sys
import replay_db
import hashlib
import multiprocessing.dummy as mt

def sha256sum(file_object, chunk_size=4096):
	hashobj=hashlib.sha256()
    while True:
        data = file_object.read(chunk_size)
        if not data:
            break
        hashobj.update(data)
	return hashobj.digest()

class SyncObject(object):
	def __init__(self,name,func,filterfunc=lambda x: return True):
		self.name=name
		self.func=func
		self.filterfunc=filterfunc

class BardDB(object):
	def __init__(self,rootdir): #decide if multiple repdb files in a dir or one repdb file with prefixes in the keys
		self.rootdir=rootdir
		if(not os.path.isdir(self.rootdir)):
			os.makedirs(self.rootdir,exist_ok=True)
		self.contenthash=replay_db.ReplayDB(os.path.join(self.rootdir,"_contenthashes.repdb"))
		self.pider=path_identifier.PathIdentifier()
		self.syncdbs={}
		
	def sync(filenameiterator,syncobj=None):
		syncdb=None
		if(syncobj is None):
			pass
		elif(name in self.syncdbs):
			syncdb=self.syncdbs[syncname]
		else:
			syncdb=self.syncdbs.setdefault(syncname,replay_db.ReplayDB(os.path.join(self.rootdir,"%s.repdb" % (syncname))))

		#todo: count first.  Count the number of files not in the contenthash or files with a contenthash with no entry in the syncdb. 
		#todo: ignore the syncdb file, and the contenthashes file.  Basically ignore anything right underneath a barddb
		for fn in filenameiterator:
			fnid=self.pider.path2id(fn)
			if(fnid not in self.contenthash):
				self.contenthash[fnid]=sha256sum(fn)

			chash=self.contenthashes[fnid]
			if(syncobj is not None and chash not in syncdb):
				value=syncobj.func(fn)
				syncdb[chash]=value

if __name__=="__main__":
	
