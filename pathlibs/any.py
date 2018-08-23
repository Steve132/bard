from _pathlib import pathfunc
import hashlib

@pathfunc('/any/contenthash')
def any_contenthash(key,value):
	def sha256py(fn):
		block_size=1 << 16
		ho=hashlib.sha256()
		with open(fn, 'rb') as f:
			for chunk in iter(lambda: f.read(block_size), b''):
				ho.update(chunk)
		return ho.hexdigest()
	return sha256py(key[1])

@pathfunc('/any/insert')
def compute_path_any_all(key,value):
	return '1'
