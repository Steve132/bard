#!/usr/bin/env python

import mimetypes
import hashlib
import sqlite3
import os.path,os
import imp

if(not mimetypes.inited):
	mimetypes.init()
	
def get_mimetype(fn):
	if(os.path.isdir(fn)):
		a="directory/unknown"	#TODO: add different types here like project,bundle,package,whatever.
	elif(os.path.isfile(fn)):
		a=mimetypes.guess_type(fn)[0]
	else:
		return None
	return a.split('/')
	
def choice(st):
	try:
		inputa=raw_input
	except NameError:
		inputa=input
	c=inputa(st)
	return True if (c.lower()=='y' or c == '') else False
				
class Fingerprint(object):
	def __init__(self,hashval=None):
		self.hexhash=hashval
	
	def readiteratefile(fn,sz):
		keep_going=True
		while(keep_going):
			nextbatch=f.read(sz)
			if(len(nextbatch) != sz):
				keep_going=False
			yield nextbatch

	def readiteratedir(fn,sz):
		for root, dirs, files in os.walk(fn):
			for name in files:
				for s in Fingerprint.readiteratefile(os.path.join(root, name),sz):
					yield s
					
	def default(typ,fn,sz):
		if(typ[0] is 'directory'):
			ri=Fingerprint.readiteratedir(fn,sz)
		else:
			ri=Fingerprint.readiteratefile(fn,sz)
		return ri
		
	def __str__(self):
		return self.hexhash
		
class Entry(object):
	def __init__(self,repo,fn,type=None,metadata=None,fingerprint=None):
		self.repo=repo
		self.datapath=fn
		if(not type):
			type=self.compute_type()
		self.type=type
		if(not metadata):
			self.metadata={}
			metadata=self.compute_metadata()
		self.metadata=metadata
		if(not fingerprint):
			fingerprint=self.compute_fingerprint()
		self.fingerprint=fingerprint
		
	def compute_fingerprint(self):
		sz=1<<18
		
		try:
			ri=self.repo.overrides.fingerprint(self.type,self.datapath,self.metadata,sz)
		except:
			#todo: add plugin architecture here
			ri=Fingerprint.default(self.type,self.datapath,self.metadata,sz)
			
		s2=hashlib.sha256()
		for f in ri:
			s2.update(f)
		return Fingerprint(s2.hexdigest())
	def compute_type(self):
		return get_mimetype(self.datapath)
	def compute_metadata(self):
		try:
			return self.repo.overrides.metadata(self.type,self.datapath)
		except:
			#todo: add plugin architecture here
			s=os.stat(self.datapath)
			k=dir(s)
			return self.metadata | dict(zip(k,map(lambda x: getattr(s,x),k))) #this should be redone but its cool (union)
	def project(self):
		try:
			return self.repo.overrides.project(self)
		except:
			tags=self.metadata['tags']
			args=tags.extend([self.type[0],self.type[1],os.path.basename(self.datapath)])
			return os.path.join(*args)
	
class Database(object):
	def __init__(self,dbfile):
		self.conn=sqlite3.connect(dbfile)
			
		self.curs=self.conn.cursor()
		self.curs.execute('''CREATE TABLE IF NOT EXISTS entries (fingerprint TEXT PRIMARY KEY ASC,type TEXT,datapath TEXT,metadata BLOB)''')
		
	def get(self,entry):
		self.curs.execute("SELECT (fingerprint,type,datapath,metadata) FROM entries WHERE fingerprint=?",(entry.fingerprint,))
		result=c.fetchone()
	def __del__(self):
		self.conn.commit()
		self.conn.close()
		
class Repository(object):
	def __init__(self,currentdirectory):
		self.rootdir=Repository.findroot(os.path.abspath(currentdirectory))
		self.barddir=os.path.join(self.rootdir,'.bard')
		self.database=Database(os.path.join(self.barddir,'entrydb.sqlite'))
		
		try:
			self.overrides=imp.load_module('bardoverrides',open(os.path.join(self.barddir,'overrides.py'),'r'))
		except:
			self.overrides=imp.new_module('bardoverrides')
		
		
	def findroot(currentdirectory):
		def findrootr(currentdirectory):
			if(os.path.exists(os.path.join(currentdirectory,'.bard'))):
				return currentdirectory
			parent=os.path.dirname(currentdirectory)
			
			if(parent==currentdirectory):
				return None
			else:
				return findrootr(parent)
		r=findrootr(currentdirectory)
		if(r==None):
			if(choice("'%s' does not seem to be a valid bard repository.  Would you like to create one here?[Y/N]" % currentdirectory)):
				os.makedirs(os.path.join(currentdirectory,'.bard'))
				r=currentdirectory
			else:
				raise RuntimeError("No bard repository discovered")
		return r
	def add(self,fn,options):
		e=Entry(self,fn)
		
		
if(__name__=="__main__"):
	import sys
	import argparse
	
	parser = argparse.ArgumentParser()
	parser.add_argument('barddir',help='the directory containing the bard repository')
	parser.add_argument('command',help='the bard command to run')
	args=parser.parse_args()
	
	repo=Repository(args.barddir)
	
