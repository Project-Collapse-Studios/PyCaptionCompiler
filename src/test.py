from charset_normalizer import from_bytes

with open("../Portal-Singularity-Collapse/psc/resource/psc_english.txt", "rb") as file:
    a = from_bytes(file.read())

print(a.best().encoding)

import pycaptioncompiler.compiler as compiler

a = compiler.Subtitles.from_path("../Portal-Singularity-Collapse/psc/resource/cc_src/subtitles_english.txt")
with open("test.dat", "wb") as f:
    f.write(a.serialize())
#print(a._createblocks()[0].line_data[0].offset)