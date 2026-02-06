# PyCaptionCompiler
A rewritten caption compiler for Source File games in Python

### Run with -h to get information on how to use this program.

## This repository is also houses the main library.
This library is used to compile captions natively in Python without calling a separate executable. In order to use this library you have to install it via pip, or add it to requirements.txt:
`pip install git+https://github.com/Project-Collapse-Studios/PyCaptionCompiler.git`

Then you can use this library as such:
```py
from pycaptioncompiler import Subtitles # Subtitles is the compiler class

subs = Subtitles.from_path("C:/path/to/file/file.txt") # Will open the file and handle encoding, this is the recommended option
subs = Subtitles.from_file(file) # An already opened file
subs = Subtitles.from_keyvalues(<srctools.KeyValues>) # From an already parsed file with srctools.KeyValues

with open("C:/subtitles_out.dat", "wb") as f:
    f.write(subs.serialize()) # Calling serialize actually compiles the file and serializes it, returning it.
```
