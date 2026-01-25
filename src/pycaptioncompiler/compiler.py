"""Houses the main class"""

from srctools import Keyvalues
from pathlib import Path
from io import StringIO
from charset_normalizer import from_path
from struct import pack
from logging import getLogger
from binascii import crc32

M_LOGGER = getLogger("[Main]")

# Constants
MAGIC_KEYWORD = b"VCCD"
VERSION = 1
BLOCK_SIZE = 8192


def GetLineSized(crc_len: dict[int, int], size: int) -> tuple[int | None, int]:
    """Get the hash of the largest line that has the length of less or equal of size, then delete it from crc_len"""
    max_size = 0
    chash = None
    for crchash in crc_len.keys():
        if crc_len[crchash] > max_size:
            max_size = crc_len[crchash]
            chash = crchash

    if chash:
        del crc_len[chash]

    return (chash, max_size)


class LineData:
    def __init__(self, hash_:int, offset:int, len_: int):
        self.hash = hash_
        self.offset = offset
        self.len = len_

class BlockData:
    def __init__(self):
        self.line_data: list[LineData] = []
        self.block= bytes()

    def AddLine(self, linehash: int, bytedata: bytes):
        ldata = LineData(linehash, len(self.block), len(bytedata))
        self.line_data.append(ldata)
        self.block += bytedata

    def Fill(self):
        self.block += bytes(BLOCK_SIZE - len(self.block)) # Fill up to BLOCK_SIZE with \0
        

class Subtitles:
    def __init__(self, kv_file: Keyvalues):

        self.logger = getLogger("[Subtitles]")

        kv_file = kv_file.find_key("lang")
        self.lang = kv_file["Language"]

        self.lines: dict[str, str] = {}
        for cc_line in kv_file.find_block("Tokens"):
            self.lines[cc_line.real_name] = cc_line.value

    def _createblocks(self) -> list[BlockData]:

        crc_line: dict[int, bytes] = {} # Hash: line
        crc_strlen = {} # Hash: line length (used for packing)
        
        for name, line in self.lines.items():
            name = crc32(name.lower().encode()) # Source uses 0xFFFFFFFF, no need to do bitwise and
            line = line.encode("utf-16le") + pack('h', 0)

            crc_line[name] = line
            crc_strlen[name] = len(line)
    
        # Pack into blocks

        blocks: list[BlockData] = []

        while len(crc_strlen):
            
            # Fill block by block, try to pack as many lines as you can, starting with the largest one left
            block = BlockData()
            remaining_size = 8192
            while remaining_size:
                linehash, size = GetLineSized(crc_strlen, remaining_size)
                if not linehash:
                    block.Fill() # Complete block by filling with \0 chars
                    break # No lines left of this size to pack
                
                line = crc_line[linehash]
                block.AddLine(linehash, line)
                remaining_size -= size
            
            blocks.append(block)

        return blocks


    def _createdirectory(self, blocks: list[BlockData]) -> bytes:
        """Create the directory structure: 
        Directory {
    	    Dir_entry {
    	    	crc32hash (Uint): a crc32 checksum of the sound name
    	    	block_number (Uint): number of the block it sits in
    	    	block_offset (Unsigned short): offset where this line starts in the block
    	    	string_length (Unsigned short): Length of the string
    	    }

    	    Dir_entry { 
    	    	...
    	    }
        }"""

        directory = bytearray()

        for i in range(len(blocks)):
            block = blocks[i]
            for linedata in block.line_data:
                directory += pack("I", linedata.hash)
                directory += pack("I", i)
                directory += pack("H", linedata.offset)
                directory += pack("H", linedata.len)

        return bytes(directory)

    
    def serialize(self) -> bytes:
        """Serialize to a .dat file format."""
        self.logger.info("Begin serializing...")
        file = bytearray()

        blocks = self._createblocks()
        directory = self._createdirectory(blocks)

        # HEADER
        file += MAGIC_KEYWORD

        # Version
        file += pack("i", VERSION)

        # Number of blocks
        file += pack("i", len(blocks))

        # Blocksize
        file += pack("i", BLOCK_SIZE)

        # Directory size - amount of entries
        file += pack("i", len(self.lines.keys()))

        # Block 0 offset
        cur_len = len(file) # Our current length
        cur_len += len(directory) + 4 # Add 4 because what we'll pack in a bit, also counts

        offset = cur_len // 512
        offset = (offset + 1) * 512
        file += pack("i", offset)


        # DIRECTORY
        file += directory

        file += bytes(offset - cur_len) # Fill the rest with \0

        # BLOCKS

        for block in blocks:
            file += block.block


        return file



    @staticmethod
    def from_kvs(keyvalues: Keyvalues):
        """Construct from keyvalues."""
        return Subtitles(keyvalues)

    @staticmethod
    def from_file(file: StringIO):
        """Construct from an opened (in text read mode) file."""
        kv = Keyvalues.parse(file.read())
        return Subtitles.from_kvs(kv)

    @staticmethod
    def from_path(str_or_bytes_path: str|Path):
        """Construct from a path to the file. Automatic encoding detection included."""
        matches = from_path(str_or_bytes_path)
        encoding = matches.best().encoding

        if encoding not in ("utf-16", "utf_16"):
            M_LOGGER.warning(f"File {str_or_bytes_path}, detected encoding: {encoding}, UTF-16LE is recommended!")

        with open(str_or_bytes_path, "r", encoding = encoding) as file:
            Subtitles_ = Subtitles.from_file(file)
        
        return Subtitles_