import sys,os,os.path,subprocess
import platform
import json

systemname=platform.system().lower()
if(systemname=="linux"):
	class PathIdentifier(object):
		def __init__(self):
			self.dev2uuidroot={}
			
			result=subprocess.check_output(["lsblk","--json","-o","partuuid,mountpoint,maj:min"])
			result=json.loads(result)
			for device in result["blockdevices"]:
				dev=device["maj:min"]
				rt=device["mountpoint"]
				uuid=device["partuuid"]
				devmaj,devmin=dev.split(":")
				dev=(int(devmaj) << 8) | int(devmin)
				self.dev2uuidroot[dev]=(uuid,rt)

		def path2id(self,path):
			abspth=os.path.abspath(path)
			st=os.lstat(path)
			uuid,rt=self.dev2uuidroot[st.st_dev]
			path=os.path.relpath(abspth,rt)
			return (uuid,path,st.st_mtime)
			
if(systemname=="windows"):
	class PathIdentifier(object):
		def __init__(self):
			self.dev2uuidroot={}
			#use mountvol and parse the output to find the partuuid and drive letter
			#use
			
		def path2id(self,path):
			abspth=os.path.abspath(path)
			#use abspath to find drive letter 
			mtime=os.path.getmtime(path)


