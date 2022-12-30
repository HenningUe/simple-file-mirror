# simple-file-mirror
A simple  - one way only - file mirroring package


In fact, it is more like a file update mechanism. 
Update actions are:
* Source file is present, destination missing, not tagged -> Copy.
* Source file is present, destination missing, tagged -> [No action].
* Source file is present, destination present-> [No action].
* Source file is missing, destination present-> [No action]

'Tagging' is done via a json-file, which trackes files already copied.
