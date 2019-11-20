#!/usr/bin/env python
import os
import os.path
import imghdr
import hashlib
import PIL.ExifTags
import Image
from datetime import datetime
import replay_db
import time
import sys
import multiprocessing
import argparse

class progress_estimator(object):
	def __init__(self,totalobjs,sofar=0):
		self.lastclock=time.clock()
		self.firstclock=self.lastclock
		self.total=totalobjs
		self.sofar=sofar
		self.processed=0
		
	def update(self,amount=1,display=False):
		self.sofar+=amount
		self.processed+=amount
		nc=time.clock()
		#if(nc-self.lastclock > 2.0):
		if(True):
			elapsed=nc-self.firstclock
			left=self.total-self.sofar
			rate=self.processed / elapsed
			
			sys.stderr.write("%d / %d files processed...estimated %f minutes remaining\r" % (self.sofar,self.total,left/(rate*60.0)))
			self.lastclock=nc

	def done(self):
		return self.sofar >= self.total

def sha256py(fn):
	block_size=1 << 16
	ho=hashlib.sha256()
	with open(fn, 'rb') as f:
		for chunk in iter(lambda: f.read(block_size), b''):
			ho.update(chunk)
	return ho.hexdigest()

def image_metadata(fn):
	if(not imghdr.what(fn)):
		return {}
	imgmeta={}
	try:
		a=Image.open(fn)
	except:
		return {}
	
	imgmeta['dimensions']=a.size
	
	if('exif' in a.info):
		exiftags=dict([(PIL.ExifTags.TAGS.get(k,'Unknown'),v) for k,v in a._getexif().iteritems()])
		dout=None
		if('DateTime' in exiftags):
			dout=exiftags['DateTime']
		elif('DateTimeOriginal' in exiftags):
			dout=exiftags['DateTimeOriginal']
		elif('DateTimeDigitized' in exiftags):
			dout=exiftags['DateTimeDigitized']
		try:
			dto=datetime.strptime(dout,"%Y:%m:%d %H:%M:%S")
			imgmeta['timestamp']=(dto.year,dto.month,dto.day,dto.hour,dto.minute,dto.second)
		except:
			pass

	thumbsize=(128,128)
	a.thumbnail(thumbsize, Image.ANTIALIAS)

	imgmeta['contentstamp']=hashlib.sha256(a.tobytes()).hexdigest()
	imgmeta['type']='img'
	
	imgmeta['idhash']=imgmeta['contentstamp']
	imgmeta['sortkey']=(imgmeta['dimensions'],imgmeta.get('timestamp',(0,0,0,0,0,0)))
	return imgmeta

def generic_metadata(fn):
	md={}
	md['extension']=os.path.splitext(fn)[1].lower()
	md['mtime']=os.path.getmtime(fn)
	md['size']=os.path.getsize(fn)
	md['sha256sum']=sha256py(fn)
	
	md['type']=md['extension']
	md['idhash']=md['sha256sum']
	md['sortkey']=md['mtime']
	md['fnsortkey']=fn.split(os.path.sep)[::-1]
	md['fn']=fn

	return md

def metadata(fn):
	md={}
	
	md.update(generic_metadata(fn))
	mdfuncs=[image_metadata]

	for mdf in mdfuncs:
		try:
			md.update(mdf(fn))
		except Exception as e:
			sys.stderr.write("Error processing file:%s\n%s" % (fn,e))
	
	return md

def compute_incoming_filedata_db(rpdb,files):
	total=len(files)
	sofar=0
	pgress=progress_estimator(total,sofar)

	parcount=multiprocessing.cpu_count()+1
	pool=multiprocessing.Pool(processes=parcount)

	#cs=min(len(files)//(4*parcount),1)
	cs=64
	metas=pool.imap_unordered(metadata,files,chunksize=cs)
	
	for meta in metas:
		rpdb[meta['fn']]=meta
		sofar+=1
		#sys.stderr.write("meta%d" % (sofar))
		pgress.update()
	return rpdb

	
def sorted_duplicates(rpdict):
	def entry_sort_key(kmdt):
		md=kmdt[1]
		return (md['sortkey'],md['fnsortkey'])

	uniques_lists={}
	for k,md in rpdict.iteritems():
		uhash=(md['type'],md['idhash'])
		uniques_lists.setdefault(uhash,[]).append((k,md))

	for k in uniques_lists.iterkeys():
		uniques_lists[k]=sorted(uniques_lists[k],key=entry_sort_key)
		
	return uniques_lists
		
def compute_metadata_files(rpdb,files):
	#also add any files from the filesystem_metadb from the barddir
	#don't add any files that are already in it (unless they are out of date)
	#don't add any directories

	toadd=[f for f in files if f not in rpdb and os.path.isfile(f)]
	
	rpdb=compute_incoming_filedata_db(rpdb,toadd) #compute metadata on any new files
	return rpdb

def project(sorted_duplist,outdir,tags=[]):
	pass

#The way bard works, if you include a barddb then the barddb keys and metadata are loaded too.
if __name__=='__main__':
	parser = argparse.ArgumentParser(prog='bard')
	
	sub=parser.add_subparsers(dest='command_name',help='The bard command to run')
	parser_insert=sub.add_parser('insert',help='Compute list of unique filenames to insert from rpdb')
	
	#parser.add_argument('--root','-r',default='',help='The target bard root dir',dest='bardroot')
	parser.add_argument('--db_file','-f',default=os.path.expanduser('~/.bard.rp'))
	parser.add_argument('--simulate-only','-s',default=False,type=bool,help='If simulate-only is checked, no files are written.')
	parser.add_argument('--task','-t',help='A task file to run per out of date file')

	parser_insert.add_argument('--inputfile','-f',help='The file containing the list of newline seperated filenames to be added',type=argparse.FileType('r'),required=False)
	
	argsin=parser.parse_args()
	rpdb=replay_db.replay_db(argsin.db_file)
	
	if(argsin.command_name=='insert'):
		if(not argsin.inputfile):
			fileobj=sys.stdin
		else:
			fileobj=argsin.inputfile

		files=[f.strip() for f in fileobj]
		rpdb=compute_metadata_files(rpdb,files)

		ifileshashes=sorted_duplicates(rpdb)
		typesizes={}
		totalsize=0
		for uhsh,lst in ifileshashes.iteritems():
			fn=lst[0][0]
			md=lst[0][1]
			typesizes.setdefault(md['type'],0)
			mds=md['size']
			typesizes[md['type']]+=mds
			totalsize+=mds
		
		print(sorted(typesizes.items(),key=lambda x: x[1]))
		print(totalsize)
	else:
		raise "Invalid Command"

	
	
	
	
