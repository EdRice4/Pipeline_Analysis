#!/usr/bin/python

# Import modules.
import os
from shutil import copy, move, make_archive
from sys import argv
import subprocess
import linecache
from lxml import etree as ET
from random import randrange
import pyper
from numpy import array, std

script, path_to_sequence, path_to_jModelTest, path_to_beast = argv

class NexusFile(object):

    """A class in which we will store the name and unique associated with the
       given nexus file."""

    def __init__(self, seq_file):
        self.path = str(seq_file)
        self.sequence_name = seq_file.rpartition("/")[-1]
        self.identifier = str(self.sequence_name) + '_' + 
                          str(randrange(0, 999999999))

class GetRange(NexusFile):

    """A class that will return a range of line numbers in a file
       between a user specified start and end sequence"""

    def __init__(self, range_file):
        NexusFile.__init__(self, range_file)

    # Must have empty line at end of sequences to work.
    def get_range(self, start, end):
        with open(self.path, 'r') as range_file:
            range_file = range_file.readlines()
            range_start = 0
            range_end = 0
            for num, line in enumerate(range_file, start=1):
                if start == line.lower():
                    range_start = num
                if end == line.lower():
                    range_end = num
            return range_start, range_end

class Contains(object):

    """Creates list that checks list against iterable and returns matches."""

    def contains(item, iterable):
        matching = []
        for x in item:
            matching.extend(i for i in iterable if x in i)
        return matching

class Replace(GetRange, Contains)

class jModelTest(Contains):

    """A class in which we will run and store parameters associate with
       jModelTest output."""

    def r_jModelTest_model(jModelTest_file):
        for line in jModelTest_file:
            if 'Model = ' in line:
                model_selected = line.rpartition(' ')[-1]
        return model_selected.strip([' ', '\n'])

    # Probably a better way to do this.
    def r_jModelTest_parameters(jModelTest_file):
        search = ['freqA = ', 'freqC = ', 'freqG = ', 'freqT = ', 'R(a) = ',
                  'R(b) = ', 'R(c) = ', 'R(d) = ', 'R(e) = ', 'R(f) = ',
                  'p-inv = ', 'gamma shape = ']
        jModelTest_file = enumerate(jModelTest_file.readlines())
        model = jModelTest_file.index(' Model selected: \n') # [i for i in jModelTest_file if "Model selected:" in i][0]
        parameters = filter((lambda num: num > model) and contains(search,
                             jModelTest_file), jModelTest_file)
        # parameters = contains(search, jModelTest_file)
        for num, item in enumerate(parameters):
            item = item.strip([' ', '\n']) # replace('\n', '')
            parameters[num] = item
        return parameters

# Will need this later to read and write garli.conf file.
# Run multiple threaded version?
# Could make standard.
class GarliConf(jModelTest):

    def w_garli_conf(jModelTest_file, garli_file):
        all_possible_models = {
            'JC' : ['1rate', 'equal'],
            'F81' : ['1rate', 'estimate'],
            'K80' : ['2rate', 'equal'],
            'HKY' : ['2rate', 'estimate'],
            'trNef' : ['0 1 0 0 2 0', 'equal'],
            'TrN' : ['0 1 0 0 2 0', 'estimate'],
            'K81' : ['0 1 2 2 1 0', 'equal'],
            'K3Puf' : ['0 1 2 2 1 0', 'estimate'],
            'TIMef' : ['0 1 2 2 3 0', 'equal'],
            'TIM' : ['0 1 2 2 3 0', 'estimate'],
            'TVMef' : ['0 1 2 3 1 4', 'equal'],
            'TVM' : ['0 1 2 3 1 4', 'estimate'],
            'SYM' : ['6rate', 'equal'],
            'GTR' : ['6rate', 'estimate']
        }
        configuration = garli_conf.readlines()
        model_selected = r_jModelTest_model(jModelTest_file)
        no_bootstrapreps = raw_input('How many bootstrap replications would \
                                     you like to perform? ')
        for num,item in enumerate(configuration):
            if item.find('datafname') != -1:
                item = 'datafname = %s\n' % sequence_name
                configuration[num] = item
            if item.find('ofprefix') != -1:
                item = 'ofprefix = %s\n' % identifier
                configuration[num] = item
            if item.find('bootstrapreps') != -1:
                item = 'bootstrapreps = %s\n' % no_bootstrapreps
                configuration[num] = item
            if item.find('datatype') != -1:
                item = 'datatype = nucleotide\n'
                configuration[num] = item
            if item.find('ratematrix') != -1:
                item = 'ratematrix = %s\n' % all_possible_models[str(model_selected)][0]
                configuration[num] = item
            if item.find('statefrequencies') != -1:
                item = 'statefrequencies = %s\n' % all_possible_models[str(model_selected)][1]
                configuration[num] = item
            if item.find('ratehetmodel') != -1:
                if '+G' in str(model_selected):
                    item = 'ratehetmodel = gamma\n'
                    configuration[num] = item
                else:
                    item = 'ratehetmodel = none\n'
                    configuration[num] = item
            if item.find('numratecats') != -1:
                if '+G' in str(model_selected):
                    item = 'numratecats = 4\n'
                    configuration[num] = item
                else:
                    item = 'numratecats = 1\n'
                    configuration[num] = item
            if item.find('invariantsites') != -1:
                if '+I' in str(model_selected):
                    item = 'invariantsites = estimate\n'
                    configuration[num] = item
                else:
                    item = 'invariantsites = none\n'
                    configuration[num] = item
        output.write(str(configuration))

class ToleranceCheck(object):

    """A class that can calculate statistics of data in a file separated into
       columns."""

    def __init__(self, data_file):
        self.data_file = (open(data_file, 'r')).readlines()
        # data = self.data_file.readlines()
        data = [line.split() for line in self.data_file if isinstance(line[:1], num) == True]
        cat_data = zip(*data)
        # store current sample/length
        # store previous as well

    def calculate_statistics(data):
        st_dev = []
        for i in data:
            parameter = i.pop([0])
            i = array(i)
            st_dev.extend[std(i)]
        return parameter, st_dev

# Will need this later to replce values in XML value with desired values.
# Do I have all necessary parameters?
# Could use regular expressions.
def w_beast_xml(jModelTest_file, xml_file):
    (freqA, freqC, freqG, freqT, Ra, Rb, Rc, Rd, Re, Rf, gamma_shape = 
    r_jModelTest_parameters(jModelTest_file))
    chain_length = raw_input("How long would you like to run the chain? ") # Make this standard.
    store_every = raw_input("How often would you like the chain to sample? ") # Make this standard.
    taxon_name = sequence_name.strip('.nex')
    beast_xml = xml_file.readlines()
    for num,item in enumerate(beast_xml):
        item = item.replace('PUT_NAME_OF_FILE_SANS_NEX_HERE', str(taxon_name))
        beast_xml[num] = item
    # beast_xml = ''.join(beast_xml)
    beast_xml = ET.XML((''.join(beast_xml)))
    output.write(ET.tostring(beast_xml, pretty_print = True))

# Will need this later to read sequences in nexus file and write to XML file.
def identify_taxon_and_seq(seq_file):
    sequence_start, sequence_end = get_range(seq_file)
    sequence_start += 1
    seq_file = seq_file.readlines()
    for line in seq_file:
        while sequence_start <= sequence_end:
                species_id = linecache.getline(str(path_to_sequence), int(sequence_start)).rpartition("\t")[0]
                species_sequence = linecache.getline(str(path_to_sequence), int(sequence_start)).rpartition("\t")[-1]
                data = root.find('data')
                sequence = ET.Element('sequence', id='%s' % species_id, taxon='%s' % species_id, totalcount='4', value='%s' % species_sequence)
                data.append(sequence)
                output.write('Standard_%s_.xml' % identifier)

class Beast(ToleranceCheck):

    """A class in which we will run beast and perform regular tolernace checks
       if specified by user."""

    def run_beast(tolerance):
        beast_xml = 'BEAST_XML_%s.xml' % identifier
        BEAST = 'java -jar %s %s -prefix %s -beagle -seed %s' % (path_to_beast,
                beast_xml, identifier, str(randrange(0, 999999))) # Do I need str function here?
        subprocess.call(BEAST.split())
        if tolerance == True:
            resume_beast('NAME OF BEAST LOG FILE')

    # Could be function of sample rather than time.
    def resume_beast(BEAST_log_file):
        ToleranceCheck(BEAST_log_file)
        BEAST_log_file.calculate_statistics()
        for i in st_dev:
            if i > tolerance:
                BEAST = 'java -jar %s %s -prefix %s -beagle -seed %s -resume' % 
                (path_to_beast, beast_xml, identifier, str(randrange(0, 999999)))

# To run bGMYC, must install PypeR.
def bGMYC():
    mcmc = raw_input("How long would you like to run the chain? ")
    burnin = raw_input("What would you like the burnin to be? ")
    thinning = raw_input("What would you like the thinning to be? ")
    r = pyper.R()
    r('library(bGMYC)')
    r('trees <- read.nexus("%s.trees")' % identifier)
    r('result.multi <- bgmyc.multiphylo(trees, mcmc=%s, burnin=%s, thinning=%s)' % (mcmc, burnin, thinning))
    # Checkpoint?
    r('result.spec <- bgmyc.spec(result.multi, filename=%s.txt)' % identifier)
    r('result.probmat <- spec.probmat(result.mult)')
    r('graphics.off()')
    r('pdf(result.probmat.%s)' % identifier)
    r('plot(result.probmat, trees[[1]])')
    r('dev.off()')

# Will need this later to clean up dump folder.
def clean_up():
    move("*" + str(identifier) + "*", str(identifier))
    copy(str(path_to_sequence), str(identifier))
    os.chdir(str(identifier))
    os.rename(str(sequence_name), str(identifier))
    os.chdir("..")
    archive_name = os.path.expanduser(os.path.join('~', str(identifier)))
    root_dir = os.path.expanduser(os.path.join('~', str(identifier)))
    make_archive(archive_name, 'gztar', root_dir)

# Ensure you are in home dir; if all files are dumped in one directory, easy to clean and organize.
home_dir = os.path.expanduser('~')
while os.getcwd() != home_dir:
    os.chdir(home_dir)

# User input to find sequence file and jModelTest, respectively.
script, path_to_sequence, path_to_jModelTest, path_to_beast = argv
# path_to_sequence = raw_input('Path to sequence file: ')
# path_to_jModelTest = raw_input('Path to jModelTest.jar: ')
# path_to_beast = raw_input('Path to BEAST.jar: ')

# Run jModelTest and create output file, jModelTest.out.
jModelTest = 'java -jar %s -d %s -t fixed -o jModelTest_%s_.out -s 11 -i -g 4 -f -tr 1' % (path_to_jModelTest, path_to_sequence, identifier)
subprocess.call(jModelTest.split())

# Molecular clock test?

# Write to garli.conf file.
with open('garli.conf', 'r+') as garli_conf:
    jModelTest_file = open('jModelTest_%s_.out' % identifier, 'r')
    output = open("garli_%s_.conf" % identifier, 'w') 
    w_garli_conf(jModelTest_file, garli_conf)
    while jModelTest_file.closed != True:
        jModelTest_file.close()
    while output.closed != True:
        output.close()

# Run garli; best to put garli in /usr/local/bin.
subprocess.call('garli')

# Prepare BEAST XML file for desired run.
with open('Standard.xml', 'r+') as beast_xml:
    jModelTest_file = open('jModelTest_%s_.out' % identifier, 'r')
    output = open('BEAST_XML_%s.xml' % identifier, 'w')
    w_beast_xml(jModelTest_file, beast_xml)
    while jModelTest_file.closed != True:
        jModelTest_file.close()
    while output.closed != True:
        output.close()

# Read sequence file and write to BEAST XML file.
with open(str(path_to_sequence), 'r') as seq_file:
    output = ET.parse('Standard.xml')
    root = output.getroot()
    identify_taxon_and_seq(seq_file)
    while seq_file.closed != True:
        seq_file.close()

# Run BEAST. Need beagle library installed (easily modified).
run_beast()

# Run bGMYC.
bGMYC()

# Copy and rename sequence file then clean up folder, creating directory and archive of latest run.
clean_up()