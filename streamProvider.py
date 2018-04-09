import subprocess
import os
import signal

#Launch a bash shell command and return the output stream
class StreamProvider:
	def getStream(self):
		PIPE = subprocess.PIPE
		
		scriptName = ['bash','openListener.sh']
		self.p = subprocess.Popen(scriptName, stdin = PIPE, stdout = PIPE, shell = False, preexec_fn=os.setsid)
	
		print "Script {} started with PID: {}".format(scriptName, self.p.pid)

		return self.p.stdout
		
	#Kill the shell process that was started earlier.
	def killStream(self):
		print "killpg PID:[{}]".format(self.p.pid)
		os.killpg(self.p.pid, signal.SIGTERM) 
		print "killpg PID: success"
