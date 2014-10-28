#!/usr/bin/env python

import mimetypes
import os.path,os
import imp
import string
import multiprocessing as mp
import glob
import argparse
from functools import partial
import string
from copy import copy

if(not mimetypes.inited):
	mimetypes.init()
verbose=False
def get_mimetype(fn):
	if(os.path.isdir(fn)):
		a="directory/unknown"	#TODO: add different types here like project,bundle,package,whatever.
	elif(os.path.isfile(fn)):
		a=mimetypes.guess_type(fn)[0]
	else:
		return ''
	return a.split('/') if a else ''
	
def choice(st):
	try:
		inputa=raw_input
	except NameError:
		inputa=input
	c=inputa(st)
	return True if (c.lower()=='y' or c == '') else False
	
def pathify(src):
	fro=string.whitespace+string.punctuation+os.sep
	to='_'*len(string.whitespace)+'.'*len(string.punctuation)+os.sep
	return src.translate(str.maketrans(fro,to))

bard_commands={}
def is_bard_command(f):
	bard_commands[f.__name__]=f
	return f

	
@is_bard_command
def insert(src,dst_root,tags):
	ifunc=find_nearest_command_function('insert',dst_root)
	if(verbose):
		print('Attempting to insert "%s"' % (src))
	dresult=ifunc(src,dst_root,tags)
	if(dresult):
		funcout=dresult[1]
		print('Success..now copying to "%s"' %(dresult[0]))
		funcout()
			

def dispatch(src,command,root,tags):
	if(command in bard_commands):
		bard_commands[command](src,root,copy(tags))
	
	
	
	
bardrootcache={}	
def find_nearest_bardroot(currentdirectory):
	global bardrootcache
	def findrootr(currentdirectory):
		if(os.path.exists(os.path.join(currentdirectory,'.bard'))):
			return currentdirectory
		parent=os.path.dirname(currentdirectory)
		
		if(parent==currentdirectory):
			return None
		else:
			return findrootr(parent)
	if(currentdirectory not in bardrootcache):
		r=findrootr(currentdirectory)
		if(r==None):
			if(choice("'%s' does not seem to be a valid bard repository.  Would you like to create one here?[Y/N]" % currentdirectory)):
				os.makedirs(os.path.join(currentdirectory,'.bard'))
				r=currentdirectory
			else:
				raise RuntimeError("No bard repository discovered")
		bardrootcache[currentdirectory]=r
	return bardrootcache[currentdirectory]

	

#The forwarding rules re-run the dispatch with a different dstroot
#The bard dispatch walks UP the directory structure looking for an insert() function in .bard, then calls it with the given dstroot and tags.
dstroot_command_cache={}
command_defaults={'insert':None}
def find_nearest_command_function(command,dstroot):
	global dstroot_command_cache
	cmdkey=dstroot+':::'+command
	if(cmdkey not in dstroot_command_cache):
		bardroot=os.path.join(find_nearest_bardroot(dstroot),'.bard')
		if(bardroot):
			mod=imp.load_source(pathify(cmdkey),os.path.join(bardroot,'commands.py'))
			ifunc=getattr(mod,command,command_defaults[command])
		else:	
			ifunc=command_defaults[command]
		dstroot_command_cache[cmdkey]=ifunc
	return dstroot_command_cache[cmdkey]
			
def recursive_dir_iterator(files):
	
	for f in files:
		g=glob.glob(f)
		if(len(g)==0):
			print("%s did not match any known files." % f)
		for fn in glob.glob(f):
			if(not os.path.isdir(fn)):
				yield fn
			else:
				for (root,dirs,files) in os.walk(fn):
					for fn1 in files:
						yield os.path.join(root,fn1)
						

		
def parallel_dispatch(files,command,root,tags,recursive=False,threads=None,verbosity_flag=False):
	tags=','.join(tags)
	tags=tags.split(',')
	tags=dict([ t.split('=') if '=' in t else (t,None) for t in tags])
	global verbose
	verbose=verbosity_flag
	pool=mp.Pool(threads)
	if(recursive==True):
		files=recursive_dir_iterator(files)
	internalfunc=partial(dispatch,command=command,root=root,tags=tags)
	pool.map(internalfunc,files)

	
if(__name__=="__main__"):
	import sys
	import argparse
	
	parser = argparse.ArgumentParser()
	parser.add_argument('command',help='the bard command to run',choices=list(bard_commands.keys()))
	parser.add_argument('-r','--root',help='the directory containing the target bard repository',default='.')
	parser.add_argument('-R','--recursive',help='recursively traverse inputs if they are directories',action='store_true')
	parser.add_argument('-t','--tags',help='file tags',action='append')
	parser.add_argument('-k','--threads',type=int,help='The number of parallel cores',default=None)
	parser.add_argument('-v','--verbose',help='Turn on output messages',action='store_true',dest='verbosity_flag')
	#parser.add_argument('file',help='the files to import',nargs=argparse.REMAINDER)
	args,inputs=parser.parse_known_args()
	args=vars(args) #convert to dict
	
	parallel_dispatch(inputs,**args)
	