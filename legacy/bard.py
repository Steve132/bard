#!/usr/bin/env python
import sys
import os,os.path
import progress
import logging
import replay_db
import argparse
import multiprocessing
import itertools

from pathlibs import *
import pathlibs

def filekey(path,lastmodified=None):
	def normalize_path(path):
		#Should this use hard drive information?
		path=os.path.abspath(path)
		return path
	def get_volume(path):
		return None

	path=normalize_path(path)
	volid=get_volume(path)

	if(lastmodified is not None):
		return (volid,path,lastmodified)
	else:
		try:
			return (volid,path,int(os.path.getmtime(path)))
		except os.error:
			return (volid,path,None)

def keyvalidhere(k):
	fn=k[1]
	return os.path.exists(fn) and os.path.isfile(fn)

def compute_helper(expaths,key,value,*args,**kwargs):
	for p in expaths:
		value[p]=pathlibs.registry.compute_path(key,value,p,*args,**kwargs)
	return value

def verify_all_paths(dbentry,paths):
	for p in paths:
		if(p not in dbentry):
			return False
	return True
#https://stackoverflow.com/questions/11312525/catch-ctrlc-sigint-and-exit-multiprocesses-gracefully-in-python
#Also consider dumping around writeback on replaydb in order to prevent termination

def update_paths(rpdb,filelist,paths,argsin):
	if(paths == None or len(paths)==0):
		paths=['/any/insert'] #pathlibs.registry.get_default_paths_from_type(key)
	paths=pathlibs.registry.expand_paths(paths)
	#print(paths)
	keylist=list([filekey(fn.strip()) for fn in filelist])
	
	keylist=[k for k in keylist if keyvalidhere(k) and k is not argsin.db_file]
	keylist=[k for k in keylist if ((k not in rpdb) or not verify_all_paths(rpdb[k],paths))]
	p=None if not argsin.progress else progress.progress_estimator(len(keylist))
	ccount=multiprocessing.cpu_count() if argsin.threaded else 1
	chunksize=len(keylist)//ccount
	pool=multiprocessing.Pool(ccount)
	#TODO fix this for multiprocessing
	args=[]
	kwargs={}

	def iterapply(kl):
		for k in kl:
			yield k,pool.apply_async(compute_helper,tuple([paths,k,rpdb.get(k,{})]+list(args)),kwargs)

	for k,result in iterapply(keylist):
		#print("Processing %s " % (str(k)))
		writeback=result.get()
		if(writeback != None):
			rpdb[k]=writeback

		if(p != None):
			p.update()
	return p
			
#The way bard works, if you include a barddb then the barddb keys and metadata are loaded too.
if __name__=='__main__':
	parser = argparse.ArgumentParser(prog='bard')
	
	sub=parser.add_subparsers(dest='command_name',help='The bard command to run')
	parser_insert=sub.add_parser('insert',help='Compute list of unique filenames to insert from rpdb')
	
	#parser.add_argument('--root','-r',default='',help='The target bard root dir',dest='bardroot')
	parser.add_argument('--db_file','-db',default=os.path.expanduser('~/.bard.rp'))
	parser.add_argument('--simulate-only','-s',default=False,type=bool,help='If simulate-only is checked, no files are written.')
	parser.add_argument('--task','-t',help='A task file to run per out of date file')

	#parser_insert.add_argument('inputfile',help='The file containing the list of newline seperated filenames to be added',type=argparse.FileType('r'),nargs='+')
	parser_update=sub.add_parser('update',help='Update specific properties of the files')
	parser_update.add_argument('--no-threaded',help='Use multiprocessing',action='store_true')
	parser_update.add_argument('--progress',help='Show progress report',action='store_true')
	parser_update.add_argument('paths',help='The property paths to update for these files',nargs='?',action="append")

	parser_list=sub.add_parser('list',help='List files satisfying certain critera')
	#parser_update.add_argument('paths',help='The property paths to update for these files',nargs='?')
	
	argsin=parser.parse_args()
	rpdb=replay_db.ReplayDB(argsin.db_file)
	
	if(argsin.command_name=='insert'):
		pass#update_paths(rpdb,sys.stdin,['/any/insert'],argsin)	
	elif(argsin.command_name=='update'):
		update_paths(rpdb,sys.stdin,argsin.paths,argsin)
	elif(argsin.command_name=='list'):
		for k in rpdb:
			print(k[1])
	else:
		raise Exeption("Invalid Command")

	
	
