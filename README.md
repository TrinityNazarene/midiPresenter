# midiPresenter
###### Joseph Weber
###### 2015-03-28

midiPresenter is a tool written in python to generate midi signals based on activity on the file system.

- An OSX utility called `fs_usage` is used to listen to every file that is opened on the filesystem by a given process.
- A .csv file is used to hold a mapping between video filename and an integer midi signal.
- A python library called `python-rtmidi` is used to generate the midi signal.
- OSX has a built-in feature that will take the midi signal and send it over the network to another computer.

midiPresenter joins these different parts together. It also provides a UI to easily see what files are being opened and set a new mapping for the opened file.

## Code layout
I over-engineered this a little bit, but it seems to work well.

midiPresenter.py is the main program. This program will:

1. Launch `streamProvider.py` which will start the `fs_usage` Mac utility program. This program is stared using the `openListener.sh` script.
1. Create a python Queue object to hold output from fs_usage
1. Spin off a thread in `eventListener.py` which will listen to the pipe output stream from `fs_usage` (#1) and place it on the queue (#2).
1. Load the config .csv file in `configHandler.py`. The config file holds file name -> midi note mappings.
1. Initialize the user interface with a "model" `uiModel.py` that handles relation between the UI thread and the rest of the program.
1. Initialize the user interface itself.
1. Spin off a thread in `queueProcessor` that will receive messages in the Queue from (#2), get the mapping for the message from the config in (#4), send the response to the `midiHandler.py` and pass the activity message to the `uiModel` from (#5).
1. Once things are initialized, the UI is started on the main thread and execution passes to `ui.py`.
1. When the UI is closed, midiPresenter will cleanup by killing off the `fs_usage` program from (#1).

Only one instance of `fs_usage` can run at a time, so if #9 fails the process will need to manually be found and killed.

The `openListener.sh` script will search for an instance of ProPresenter. If the PID for propresenter is found, it will be used by `fs_usage`. `openListener.sh` also filters the output of `fs_usage`. It uses grep to only output lines that contain the "*open*" word, indicating that a file is being opened, and it only outputs files that are in a "*video*" directory. This avoids being overwhelmed by too much activity.


The UI provides two buttons.
1. Active/Inactive will toggle the state of the program
1. Quit

The UI provides a pane for output messages. Each message is for a file being read on the filesystem. There are four posibilities.
1. The UI state is Inactive and the file is skipped.
1. The file is does not have a registered mapping.
1. The file is registered but the midi note was the midi signal sent most recently. The note is skipped.
1. The file is registered and the midi note is sent.

Clicking on an output message for a file will open up a new Dialog where a mapping midi number can be set.

`midiHandler.py` provides a function that will generate a midi command using `python-rtmidi`.

midi notes are represented as integers 1-127 inclusive.

RtMidi is a C program that provides a cross-platform API for manipulating MIDI input and output.
python-rtmidi is the python wrapper for this program. I had to install the [python-rtmidi](https://pypi.python.org/pypi/python-rtmidi "python-rtmidi") package on the church Mac manually.


## Run Notes

The fs_usage utility requires sudo permissions by default
To allow fs_usage from non-sudo in Mac OSX:
```
"sudo visudo"
add line at bottom of file
TrintyTech ALL=(ALL) NOPASSWD: /usr/bin/fs_usage
```


To start the Mac remote midi feature
- Audio MIDI Setup
- Window -> Show MIDI Window
- Network
- Connect to lighting/connect to slides
- Live Routings on slides
-- Right: IAC Driver Bus 1
-- Left -blank-
- Live Routings on lights
-- Right -blank-
-- Left -blank-

- TheLightingController -> Preferences -> MIDI in enable -> Session 1


## TODO List


Need to fix double click issue where two dialogs pop up.

When double clicking on a file already mapped, the input box should be pre-populated with the current midi value.

Stress test close scenarios to ensure fs_usage is always killed.

Maybe somehow wrap all python files into a single executable?

Provide better and more flexible filtering of the fs_usage output. Currently grep is used for this task.

Perhaps cleanup of the midiHandler.py script and rtmidi usage. Currently create a new rtmidi instance with every note.
I havent noticed any problem with this, but it may not be ideal.
