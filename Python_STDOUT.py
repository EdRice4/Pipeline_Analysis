import subprocess
from random import randrange

path_to_beast = 'jModelTest.jar'
identifier = 'Homo_erectus' + str(randrange(0, 999999999))

def run_beast():
    beast_xml = 'Cerapachys_ULTIMATE_NOTRM_UNDERSCORE.nex'
    BEAST = 'java -jar %s -d %s -t fixed -o jModelTest_%s_.out -s 11 -i -g 4 -f -tr 1' % (path_to_beast, beast_xml, identifier)
    BEAST_run = subprocess.Popen((BEAST).split(' '), stderr=subprocess.STDOUT, 
                stdout=subprocess.PIPE)
    out, err = BEAST_run.communicate()
    return out

print run_beast()