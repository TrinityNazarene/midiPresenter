import threading

#Listen to a stream. Place any incoming messages in the given queue.
#Automatically runs as its own thread.
class EventListener:

	def __init__(self, stream, queue):

		self._stream = stream #input stream
		self._queue = queue #output queue

		def _readStream(self):
			
			while True:
				#readline will wait for new string
				line = self._stream.readline()
				if line:
					#cleanup the string
					parsed = _parseLine(line)
					#place on queue
					self._queue.put(parsed)

		def _parseLine(line):
			return line.strip()
		
		#startup a new thread
		self._thread = threading.Thread(target = _readStream, args = (self,))
		self._thread.daemon = True #won't prevent shutdown.
		self._thread.start()
