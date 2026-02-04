"""Houses the main program file"""

from pycaptioncompiler import Subtitles
from pcslogger import Logger, Level
from sys import argv
import argparse
from pathlib import Path

LOG_LEVEL = Level.DEBUG
LOG_PATH = Path(argv[0]).with_name("pycaptioncompiler.log")
AppLogger = None

def main():
    parser = argparse.ArgumentParser(
        "Caption Compiler",
        description="Caption compiler program remade in python, for Source Engine games."
    )

    parser.add_argument(
        "-v", "--verbose",
        help="Be verbose, log more information.",
        action="store_true",
        dest="verbose",
    )

    parser.add_argument(
        "-o", "--output",
        help="Output directory. Not required, if not specified, output file will be in the same location as the source file.",
        dest="outpath",
        required=False,
        default=None
    )

    parser.add_argument(
        "source_file",
        help="The source file housing given subtitles."
    )

    result = parser.parse_args(argv[1:])

    global AppLogger
    AppLogger = Logger.RegisterMainApplication("Caption Compiler", result.verbose, LOG_LEVEL, True)

    Logger.EnableFileLogging(LOG_PATH)

    AppLogger.Info("Caption Compiler, Welcome!")
    AppLogger.Info(f"Verbose: {result.verbose}")
    AppLogger.VInfo(f"Logging to: {LOG_PATH}")
    
    INFILE = Path(result.source_file).absolute()
    if not INFILE.is_file():
        AppLogger.Error(f"Specified file ({INFILE}) does not exist!")
        raise FileNotFoundError


    OUTPATH = None
    if result.outpath:
        OUTPATH = Path(result.outpath).resolve()
        if not OUTPATH.is_dir():
            AppLogger.Warning(f"Specified output directory ({OUTPATH}) does not exist. Creating...")
            OUTPATH.mkdir(parents=True)
        
        OUTPATH = OUTPATH / INFILE.with_suffix(".dat").name

    else:
        OUTPATH = INFILE.with_suffix(".dat")        


    AppLogger.Info(f"INFILE: {INFILE}")
    AppLogger.Info(f"OUTFILE: {OUTPATH}")

    AppLogger.Info("Starting compile...")

    Subtitles_ = Subtitles.from_path(INFILE)

    fbytes = Subtitles_.serialize()
    
    AppLogger.Info("Finished. Saving results...")
    AppLogger.VInfo(f"Writing to file: {OUTPATH}")

    with open(OUTPATH, "wb") as f:
        f.write(fbytes)

    AppLogger.Info("Done.")

main()
