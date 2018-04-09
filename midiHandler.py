import time
import rtmidi

#function to generate a midi note
#uses the python-rtmidi library #https://pypi.python.org/pypi/python-rtmidi
#python-rtmidi should be cross-platform, but the package will need to be installed separately
def send(message):

	#this is taken from example code in the python-rtmidi docs
    midiout = rtmidi.MidiOut()
    available_ports = midiout.get_ports()
    
    if available_ports:
        midiout.open_port(0)
    else:
        midiout.open_virtual_port("My virtual output")

	#TODO: It may be better to open this port once, and then reuse it. Seems to work as is though.
    
    note_on = [0x90, int(message), 112] # channel 1, given note integer, velocity 112
    note_off = [0x80, int(message), 0]

    midiout.send_message(note_on)
    #time.sleep(0.1)
    midiout.send_message(note_off)
    
    del midiout #cleanup


if __name__ == "__main__":

	send(60)
