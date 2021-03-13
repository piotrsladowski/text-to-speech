import pyttsx3
import argparse
import os
import subprocess
import re

# Initiate the parser
parser = argparse.ArgumentParser()
# Add long and short argument
parser.add_argument("--inputText", "-i", help="specify input file", required=True)
parser.add_argument("--separator", "-s", help="specify string to separate text e.g chapters")
parser.add_argument("--voice", "-v", help="select the voice - number from 0 to x (depends from installed voices in your system")
# Read arguments from the command line
args = parser.parse_args()

def sanitize(inpText):
    sanitized = re.sub("\[\d+]", "", inpText)
    if args.separator:
        sanitized = sanitized.split(args.separator)
        if len(sanitized) > 50:
            print("Your text has been splited for more than 50 parts.")
            reply = str(input("Continue? "+' (y/n): ')).lower().strip()
            if reply[0] != 'y':
                quit()
    return sanitized

def synthesize():
    print("Input file: {0}".format(args.inputText))
    baseFileName = os.path.basename(args.inputText).split('.')[0]
    engine = pyttsx3.init()

    """ RATE"""
    #rate = engine.getProperty('rate')   # getting details of current speaking rate
    engine.setProperty('rate', 150)     # setting up new voice rate

    """VOLUME"""
    engine.setProperty('volume',1.0)    # setting up volume level  between 0 and 1

    """VOICE"""
    voices = engine.getProperty('voices')   #getting details of current voice
    voiceNum = 3 # Polish - Adam
    if args.voice:
        try:
            voiceNum = int(args.voice)
        except:
            print("Invalid voice parameter")
            quit()
    engine.setProperty('voice', voices[voiceNum].id)  #changing index, changes voices. o for male

    f = open(args.inputText, 'r', encoding="utf8")
    inpText = f.read()
    sanitizedText = sanitize(inpText)
    if type(sanitizedText) is list:
        length = len(sanitizedText)
        for x in range(length):
            baseFileName = "{:02d}".format(x+1)
            midFileName = baseFileName + ".mp3"
            outFileName = baseFileName + ".opus"
            print("Generating mp3 audio file")
            engine.save_to_file(sanitizedText[x], midFileName)
            engine.runAndWait()
            engine.stop()
            f.close()
            print("Transcoding to opus 96K")
            try:
                if os.name == 'nt':
                    subprocess.call('powershell.exe "ffmpeg.exe -hide_banner -i {0} -c:a libopus -b:a 80K {1}"'.format(midFileName, outFileName), stderr=subprocess.STDOUT, shell=True)
                elif os.name == 'posix':
                    subprocess.call('ffmpeg -hide_banner -i {0} -c:a libopus -b:a 80K {1}'.format(midFileName, outFileName), stderr=subprocess.STDOUT, shell=True)
            except:
                print("Error during transcoding")
            print("Removing mp3 file")
            try:
                os.remove(midFileName)
            except:
                print("Error during removing")

            print("Finished successfully")
    else:
        midFileName = baseFileName + ".mp3"
        outFileName = baseFileName + ".opus"
        print("Generating mp3 audio file")
        engine.save_to_file(sanitizedText, midFileName)
        engine.runAndWait()
        engine.stop()
        f.close()
        print("Transcoding to opus 96K")
        try:
            if os.name == 'nt':
                subprocess.call('powershell.exe "ffmpeg.exe -hide_banner -i {0} -c:a libopus -b:a 80K {1}"'.format(midFileName, outFileName), stderr=subprocess.STDOUT, shell=True)
            elif os.name == 'posix':
                subprocess.call('ffmpeg -hide_banner -i {0} -c:a libopus -b:a 80K {1}'.format(midFileName, outFileName), stderr=subprocess.STDOUT, shell=True)
        except:
            print("Error during transcoding")
        print("Removing mp3 file")
        try:
            os.remove(midFileName)
        except:
            print("Error during removing")

        print("Finished successfully")

def is_tool(name):
    """Check whether `name` is on PATH."""
    from distutils.spawn import find_executable
    return find_executable(name) is not None

if args.inputText:
    if not is_tool("ffmpeg"):
        print("FFmpeg not found in your system.\nExiting")
        quit()
    synthesize()

    