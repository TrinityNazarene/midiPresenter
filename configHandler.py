import csv
import threading

#Manage the configuration mapping (.csv) file.
#The configuration file will identify which MIDI signal should be sent for a given file name.
#The configuration file is a simple two column .csv loaded into a python dictionary.
#Access to the dictionary is synchronized by a Lock to ensure thread safety.
class ConfigHandler:

	def __init__(self, filepath):

		self._filepath = filepath
		self._mapping = {}
		self._lock = threading.Lock()
		
		self.readMappingFromFile()

	#load the file into memory
	def readMappingFromFile(self):
		with open(self._filepath, 'r') as mapFile:
			reader = csv.reader(mapFile, delimiter = ',')
			for row in reader:
				self.addMapping(row[0], row[1])
		pass

	#dump the dictionary in memory to the file. overwrite existing file.
	def writeMappingToFile(self):
		with open(self._filepath, 'w') as mapFile:
			writer = csv.writer(mapFile, delimiter = ',')
			with self._lock:
				for key,value in self._mapping.iteritems():
					writer.writerow([key,value])

	#Given an input string, return the value found in the config file. synchronized using _lock.
	def getResponseForMessage(self, message):
		try:
			with self._lock:
				response = self._mapping[message.strip()]
		except KeyError: #return None if key not found.
			response = None
		return response
		
	#add the key, value pair to the dictionary. synchronized using _lock.
	def addMapping(self, key, value):
		print "add mapping key:[{}] value:[{}]".format(key, value)
		with self._lock:
			self._mapping[key] = value
		self.writeMappingToFile()
