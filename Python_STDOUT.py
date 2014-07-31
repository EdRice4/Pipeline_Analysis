import subprocess
import shlex
from random import randrange

path_to_beast = '../BEAST/lib/beast.jar'
identifier = 'Homo_erectus' + str(randrange(0, 999999999))

def run_beast():
    beast_xml = 'testTN93.xml'
    BEAST = 'java -jar %s -seed %s %s' % (path_to_beast, randrange(0, 999999),
            beast_xml)
    BEAST_run = subprocess.Popen((BEAST).split(' '), stderr=subprocess.STDOUT, 
                stdout=subprocess.PIPE)
    out, err = BEAST_run.communicate()
    return out
    # subprocess.call(BEAST.split())

print run_beast()