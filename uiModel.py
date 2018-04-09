import Queue

#Holder for message and state between the UI and the processor.
class UIModel:
    def __init__(self, config):
		#Queue for passing messages to the UI
        self.messageQueue = Queue.Queue()
		#State of the UI/processor
        self.active = True
		#The mapping config.
        self.config = config

    def isActive(self):
        try:
            return self.active
        except AttributeError:
            return False
    
	#Send a message to the UI for display
    def addMessage(self, message):
        self.messageQueue.put(message) 
       
	#Add a new mapping to the config
    def newMapping(self, key, value):
        self.config.addMapping(key, value)

    def getMapping(self, key):
	return self.config.getResponseForMessage(key)
