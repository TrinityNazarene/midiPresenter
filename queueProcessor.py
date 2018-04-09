import threading
import Queue
import traceback

#Process messages received from a queue and send them on as a midi signal, while also sending status messages to the UI
class QueueProcessor:

	#launches itself in a new thread
	def __init__(self, queue, config, uiModel, midiHandler):

		self._queue = queue
		self._config = config
		self._uiModel = uiModel
		self._midiHandler = midiHandler
		self._previousMessage = ""


		def _process(self):
			while True:
				try:
					messageIn = queue.get(True) #Get a message from the queue, block until something is received.
					messageIn = self.parseMessage(messageIn) #parse the message into something usable by the mapping
					messageOut = config.getResponseForMessage(messageIn) #get the value to use from the mapping for this message
					uiDisplayMessage = ''
					if(not self._uiModel.isActive()): #UI is inactive
						uiDisplayMessage = ' Skipping: Inactive.'
					elif(messageOut == None): #No output value for this message
						uiDisplayMessage = ' Skipping: NoMapping.'
					elif(self._previousMessage == messageOut): #Already sent this message
						uiDisplayMessage = ' Skipping: AlreadySent.'
					else:
						try:
							midiHandler.send('127') #scene-clear #always send 127 to ensure we do not deactivate an already-clicked button.
							midiHandler.send(messageOut)
						except:
							uiDisplayMessage = ' ERROR.'
						self._previousMessage = messageOut
						uiDisplayMessage = ' Sent.'
						
					#Format a message to display in the UI.
					uiDisplayMessage = ('Received: [{}].\nResponse: [{}].' + uiDisplayMessage).format(messageIn, messageOut)
					print uiDisplayMessage #Log to console and send to UI.
					self._uiModel.addMessage(uiDisplayMessage)

				except Queue.Empty: pass #ignore an empty Queue and try again
				except KeyboardInterrupt:
					print 'quitting QueuProcessor B'
					break
				except:
					print 'Unexpected error in queueProcessor.py'
					traceback.print_exc()
				  
		#startup a thread
		self._thread = threading.Thread(target = _process, args = (self,))
		self._thread.daemon = True #won't prevent program shutdown
		self._thread.start()

	#extract the filename out of the full file path.
	def parseMessage(self, message):
		start = message.rfind('/') + 1 #start = index of last forward slash
		end = message.find(' ', start) #end = index of first space after start
		return message[start:end]	
