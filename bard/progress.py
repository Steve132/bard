#!/usr/bin/env python
import time
import sys

class InteractiveFileObjectEstimator(object):
	def __init__(self,fo=sys.stderr):
		self.fo=fo
	def __call__(self,sofar,total,left,rate):
		self.fo.write("%d / %d files processed...estimated %f minutes remaining\n" % (sofar,total,left/(rate*60.0)))

class progress_estimator(object):
	def __init__(self,totalobjs,sofar=0,estimator=InteractiveFileObjectEstimator(sys.stderr)):
		self.lastclock=time.time()
		#print "init progress with lastclock:", self.lastclock
		self.firstclock=self.lastclock
		self.total=totalobjs
		self.sofar=sofar
		self.processed=0
		self.estimator=estimator
		
	def update(self,amount=1,display=True):
		self.sofar+=amount
		self.processed+=amount
		nc=time.time()
		#print "update progress with nc:", nc
		if((nc-self.lastclock) > 2.0):
			elapsed=nc-self.firstclock
			left=self.total-self.sofar
			rate=self.processed / elapsed
			self.estimator(self.sofar,self.total,left,rate)
			self.lastclock=nc

	def done(self):
		return self.sofar >= self.total
