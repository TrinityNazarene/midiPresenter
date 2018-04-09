#! /usr/bin/env python

#The main program code
#Initialize and begin helper threads, then launch the UI.

import Queue
import sys

import streamProvider
import queueProcessor
import eventListener
import midiHandler
import configHandler
import uiModel
import ui


if __name__ == "__main__":
	
	#write all of out output to a file -- append and line buffer
	sys.stdout = open('/Users/TrintyTech/midiPresenter/output.log', 'a',1)
	sys.stderr = sys.stdout
  
	#Create a stream from which we will receive new requests
	streamP = streamProvider.StreamProvider()
	stream = streamP.getStream()

	#Create a queue onto which we will load new requests
	queue = Queue.Queue()

	#Thread to move requests from the stream to the queue
	listener = eventListener.EventListener(stream, queue)

	#Our list of mappings -- input string to output midi note.
	config = configHandler.ConfigHandler('midiPresenterMapping.csv')
	
	#UI
	model = uiModel.UIModel(config)
	dialog = ui.UI(model)
	
	#Processing thread to do bulk of work. -- Receive incoming items from the queue, decide how they should be handled, and notify the UI.
	queueProcessor.QueueProcessor(queue, config, model, midiHandler)

	#blocking -- control passes to the UI.
	dialog.run()
	
	print 'end prog'

	#Cleanup
	streamP.killStream()
	
	sys.exit()
