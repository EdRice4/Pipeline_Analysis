from random import randrange
import os
import tempfile
import subprocess

path_to_beast = 'beast.jar'
identifier = str(randrange(0, 999999999))

def run_beast():
    beast_xml = 'testTN93.xml'
    BEAST = 'java -jar %s %s -prefix %s -beagle -seed %s -working ~/Documents/Carstens/BEAST/Test_bGMYC/' % (path_to_beast, beast_xml, identifier, str(randrange(0, 999999))) # Do I need str function here?
    BEAST_log = tempfile.NamedTemporaryFile()
    try:
        BEAST_log.write(subprocess.call(BEAST.split()))
    finally:
        BEAST_log.close()
    return BEAST_log
    # Will this code wait? I don't believe so.
    # if user_input = True:
        # delay period of time
        # run resume beast
print run_beast()