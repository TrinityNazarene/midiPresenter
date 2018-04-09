import Tkinter

#Display a simple UI with Active/Inactive state, output messages,
#and ability to click message to set new mappings.
class UI:

	def __init__(self, uiModel):
		self.uiModel = uiModel
		
	def run(self):
		#Build window
		self.root = Tkinter.Tk()

		self.root.title('MidiPresenter')

		self.root.protocol("WM_DELETE_WINDOW", self.closeCallback)

		frame = Tkinter.Frame(self.root)
		frame.grid(column=0, row=0, sticky=Tkinter.N+Tkinter.S+Tkinter.E+Tkinter.W)

		#Build buttons
		#Toggle button, switches between Active/Inacive state, call toggleCallback with every press
		self.toggle = Tkinter.Button(frame, command=self.toggleCallback)
		self.toggle.grid(row=1, column=1, sticky=Tkinter.E+Tkinter.N)
		
		#Quit button, call closeCallback with every press
		self.button = Tkinter.Button(frame, text="QUIT", command=self.closeCallback)
		self.button.grid(row=1, column=2, sticky=Tkinter.W)
		
		#Create a frame to house a scrollbar and Text area.
		frameA = Tkinter.Frame(frame,relief=Tkinter.GROOVE, bd=1)
		frameA.grid(row=2, column=1, columnspan=2, sticky=Tkinter.N+Tkinter.S+Tkinter.E+Tkinter.W)
		
		#Create a scrollbar and Text area.
		scrollbar = Tkinter.Scrollbar(frameA, orient=Tkinter.VERTICAL)
		self.mainLabel = Tkinter.Listbox(frameA,height=5, width=50, selectmode=Tkinter.EXTENDED)

		#Add the scrollbar and text area to the layout.
		scrollbar.pack(side=Tkinter.RIGHT, fill=Tkinter.Y)
		self.mainLabel.pack(side=Tkinter.LEFT, fill=Tkinter.BOTH, expand=Tkinter.YES)
		
		#Assign the scrollbar and text area to each other.
		scrollbar.configure(command=self.mainLabel.yview)
		self.mainLabel.configure(yscrollcommand=scrollbar.set)
		
		#Allow for window resizing.
		self.root.rowconfigure(0,weight=1)
		frame.rowconfigure(2,weight=1)
		self.root.columnconfigure(0,weight=1)
		frame.columnconfigure(1,weight=1)
		frame.columnconfigure(2,weight=1)
		
		#Add select and double click listeners
		self.mainLabel.bind('<<ListboxSelect>>', self.onselect)
		self.mainLabel.bind('<Double-Button-1>', self.ondouble)
		
		#Build state
		self.activate()
		
		self.checkMessageQueue()
		self.isDialogOpen = False

		#Get started
		self.root.mainloop()
		
	#Line items always come in pairs.
	#When a line item is selected, automatically select its pair as well
	def onselect(self, event):
		w = event.widget
		index = int(w.curselection()[0])
		value = w.get(index)
		if(value.startswith("    ")):
			index = index-1
		w.selection_set(index,index+1)
		
	#When a line item is double clicked, open a dialog to enter a new mapping.
	def ondouble(self, event):
		if ( self.isDialogOpen ):
			return
		try:
			self.isDialogOpen = True

			#get the widget
			w = event.widget
			index = int(w.nearest(event.y))

			#find the value
			value = w.get(index)
			if(value.startswith("    ")): #This line is the second in the pair. We want the first.
				index = index-1
			value = w.get(index)

			#Set the status to Inactive, remembering the old value for later	
			oldActive = self.uiModel.active
			self.uiModel.active = False

			#Open the new dialog and wait
			d = ValuePromptDialog(self.root, self.uiModel, value)
			self.root.wait_window(d.top)

			#Dialog was closed, revert the status back to what it was.
			self.uiModel.active = oldActive
		finally:
			self.isDialogOpen = False
		
	#We need to periodically check the messageQueue for any new messages to display.
	def checkMessageQueue(self):
		while True:
			try:
				#Check the queue for new messages, and continue immediately if none.
				message = self.uiModel.messageQueue.get(block=False)
				if message:
					self.appendLabel(message)
				else: break
			except: #Leave loop if there are no messages
				break
		#try again later
		self.root.after(500, self.checkMessageQueue)

	#Switche between inactive an active states
	def toggleCallback(self):
		if self.uiModel.active:
			self.deactivate()
		else:
			self.activate()
		
	#Add a message to the UI
	def appendLabel(self, message):
		#Message should have a newline character.
		for index, item in enumerate(message.split('\n')):
			if(index > 0): #on the second lines, insert spaces at the beginning
				self.mainLabel.insert(Tkinter.END,"    "+item)
			else: #Add the text to the mainLabel
				self.mainLabel.insert(Tkinter.END,item)
		if(self.uiModel.isActive()): #if the state is Active, autoscroll to the end.
			self.mainLabel.yview(Tkinter.END) #Set the scrollbar to the end of the label

	#Set the Button text to Active
	def activate(self):
		self.uiModel.active = True
		self.toggle.config(background="green", text="Active")

	#Set the Button text to Inactive
	def deactivate(self):
		self.uiModel.active = False
		self.toggle.config(background="red", text="Inactive")
		
	#close the window
	def closeCallback(self):
		print "closing"
		#self.root.quit()
		self.root.destroy()


#Additional dialog to gather a file mapping.
class ValuePromptDialog:

	def __init__(self, parent, uiModel, key):
		self.uiModel = uiModel

		#get the file name from the text, wrapped in parens
		key = key[key.find("[")+1:key.find("]")]
		self.key = key

		#Get current value
		value = uiModel.getMapping(key)
		if (value == None):
			value = ''
		
		top = self.top = Tkinter.Toplevel(parent)
		top.title("MIDI Key")
		#Create a label
		Tkinter.Label(top, text="Set Value For:\n" + key).pack()

		#Create a text input
		self.e = Tkinter.Entry(top)
		self.e.pack(padx=5)
		self.e.insert(0,value)

		#Create an OK button
		b = Tkinter.Button(top, text="OK", command=self.ok)
		b.pack(pady=5)

	#When OK is clicked, save the value and close the dialog.
	def ok(self):
		value = self.e.get()
		value = value.strip()

		#validation
		isValid = True
		try:
			int(value)
		except ValueError:
			isValid = False

		#don't care about empty strings
		if (value == ''): isValid = True

		if (not isValid):
			print "value is not a number: ", value
			self.e.config(background="red")
			return False

		print "value is", value

		self.top.destroy()
		
		self.uiModel.newMapping(self.key, value)

if __name__ == "__main__":

	app = Dialog()

	print 'In ui.py __name__'
