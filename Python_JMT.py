import os
from shutil import copy, move, make_archive
from sys import argv
from subprocess import Popen, STDOUT, PIPE, call
from linecache import getline
from lxml import etree as ET
from random import randrange
import pyper
from numpy import array, std

class FileMethods(object):

    """Returns the range of user specified start and end sequences."""

    def get_range(self, range_file, start, end):
        # Could remove whitespace characters.
        range_start = range_file.index(start)
        range_file = range_file[range_start:]
        range_end = range_file.index(end) + range_start
        return range_start, range_end

    def filter_output(self, output, start, end):
        output = output[start:end]
        for num, i in enumerate(output):
            output[num] = i.translate(None, ' \r\n)')
            if '(ti/tv' in i:
                tmp = (output.pop(num)).split('(')
                output.insert(num, tmp[0])
                output.append(tmp[1])
        return output

class jModelTest(FileMethods):

    """Run jModelTest and store parameters associated with output."""

    def run_jModelTest(self):
        jModelTest = 'java -jar %s -d %s -t fixed -s 11 -i -g 4 -f -tr 1' % (path_to_jModelTest, self.path)
        jMT_run = Popen(jModelTest.split(), stderr = STDOUT, stdout = PIPE)
        with open('%s' % self.JMT_ID, 'w') as output:
            for line in iter(jMT_run.stdout.readline, ''):
                print line.strip()
                output.write(line)
        jMT_run.stdout.close()

    def r_jModelTest_parameters(self, jModelTest_file):
        start, end = self.get_range(jModelTest_file, ' Model selected: \r\n', ' \r\n')
        data = self.filter_output(jModelTest_file, start + 1, end)
        parameters = []
        for i in data:
            parameter = i.rpartition('=')[0]
            value = i.rpartition('=')[-1]
            parameters.append([parameter, value])
        for i in parameters:
            self.parameters[i[0]] = i[1]
        # self.parameters[] = parameters

class Garli(jModelTest):

    """Run garli and store parameters associated with output."""

    models = {
        'JC' : ['1rate', 'equal'],
        'F81' : ['1rate', 'estimate'],
        'K80' : ['2rate', 'equal'],
        'HKY' : ['2rate', 'estimate'],
        'TrNef' : ['0 1 0 0 2 0', 'equal'],
        'TrN' : ['0 1 0 0 2 0', 'estimate'],
        'TPM1' : ['0 1 2 2 1 0', 'equal'],
        'TPM1uf' : ['0 1 2 2 1 0', 'estimate'],
        'TPM2' : ['0 1 0 2 1 2', 'equal'],
        'TPM2uf' : ['0 1 0 2 1 2', 'estimate'],
        'TPM3' : ['0 1 2 0 1 2', 'equal'],
        'TPM3uf' : ['0 1 2 0 1 2', 'estimate'],
        'K3P' : ['0 1 2 2 1 0', 'equal'],
        'K3Puf' : ['0 1 2 2 1 0', 'estimate'],
        'TM1ef' : ['0 1 2 2 3 0', 'equal'], # Remove 'I' for translate.
        'TM1' : ['0 1 2 2 3 0', 'estimate'], # Remove 'I' for translate.
        'TM2ef' : ['0 1 0 2 3 2', 'equal'],
        'TM2' : ['0 1 0 2 3 2', 'estimate'],
        'TM3ef' : ['0 1 2 0 3 2', 'equal'],
        'TM3' : ['0 1 2 0 3 2', 'estimate'],
        'TVMef' : ['0 1 2 3 1 4', 'equal'],
        'TVM' : ['0 1 2 3 1 4', 'estimate'],
        'SYM' : ['6rate', 'equal'],
        'GTR' : ['6rate', 'estimate']
    }

    def __init__(self, input_file):
        self.garli_conf = input_file.readlines()

    def w_garli_conf(self, garli_file):
        model_selected = self.parameters['Model']
        het = '+G' in model_selected
        inv = '+I' in model_selected
        model_selected = model_selected.translate(None, '+IG')
        for num,item in enumerate(garli_file):
            if item.find('datafname') != -1:
                item = 'datafname = %s\n' % self.path
                garli_file[num] = item
            if item.find('ofprefix') != -1:
                item = 'ofprefix = %s\n' % self.identifier
                garli_file[num] = item
            if item.find('bootstrapreps') != -1:
                item = 'bootstrapreps = %s\n' % no_bootstrapreps
                garli_file[num] = item
            if item.find('datatype') != -1:
                item = 'datatype = nucleotide\n'
                garli_file[num] = item
            if item.find('ratematrix') != -1:
                item = 'ratematrix = %s\n' % Garli.models[str(model_selected)][0]
                garli_file[num] = item
            if item.find('statefrequencies') != -1:
                item = 'statefrequencies = %s\n' % Garli.models[str(model_selected)][1]
                garli_file[num] = item
            if item.find('ratehetmodel') != -1:
                if het == True:
                    item = 'ratehetmodel = gamma\n'
                    garli_file[num] = item
                else:
                    item = 'ratehetmodel = none\n'
                    garli_file[num] = item
            if item.find('numratecats') != -1:
                if het == True:
                    item = 'numratecats = 4\n'
                    garli_file[num] = item
                else:
                    item = 'numratecats = 1\n'
                    garli_file[num] = item
            if item.find('invariantsites') != -1:
                if inv == True:
                    item = 'invariantsites = estimate\n'
                    garli_file[num] = item
                else:
                    item = 'invariantsites = none\n'
                    garli_file[num] = item
        with open('garli_%s.conf' % self.identifier, 'w+') as garli_output:
            for i in garli_file:
                garli_output.write(i)

    def run_garli(self):
        garli = './garli.exe garli_%s.conf' % self.identifier
        garli_run = Popen(garli.split(), stderr = STDOUT, stdout = PIPE)
        for line in iter(garli_run.stdout.readline, ''):
            print line.strip()
        garli_run.stdout.close()

# class ToleranceCheck(object):

#     """A class that can calculate statistics of data in a file separated into
#        columns."""

#     def __init__(self, data_file):
#         data = [line.split() for line in self.data_file if isinstance(line[:1], num) == True]
#         cat_data = zip(*data)

#     def calculate_statistics(self, data):
#         st_dev = []
#         for i in data:
#             parameter = i[0]
#             data = array(i[1:])
#             st_dev.append([parameter, std(i)])
#         return st_dev

# class BEAST(ToleranceCheck):

#     """Run BEAST and store parameters associated with output."""

#     def w_beast_xml(self, beast_xml):
#         chain_length = raw_input("How long would you like to run the chain? ") # Make this standard.
#         store_every = raw_input("How often would you like the chain to sample? ") # Make this standard.
#         model_selected = self.parameters[0][1]
#         het = '+G' in model_selected
#         inv = '+I' in model_selected
#         for num, item in enumerate(beast_xml):
#             if het == True:
                
#             item = item.replace('PUT_NAME_OF_FILE_SANS_NEX_HERE', str(self.sequence_name))
#             beast_xml[num] = item
#         beast_xml = ET.XML((''.join(beast_xml)))
#         output.write(ET.tostring(beast_xml, pretty_print = True))

#     def identify_taxon_and_seq(self, seq_file, beast_xml):
#         sequence_start, sequence_end = self.get_range(self, self.seq_file, '\tmatrix\n',
#                                                  '\n')
#         sequence_start += 1
#         seq_file = seq_file.readlines()
#         for line in seq_file:
#             while sequence_start <= sequence_end:
#                 species_id = getline(str(path_to_sequence), int(sequence_start)).rpartition("\t")[0]
#                 species_sequence = getline(str(path_to_sequence), int(sequence_start)).rpartition("\t")[-1]
#                 data = root.find('data')
#                 sequence = ET.Element('sequence', id='%s' % species_id,
#                                       taxon='%s' % species_id, totalcount='4',
#                                       value='%s' % species_sequence)
#                 data.append(sequence)
#                 output.write('Standard_%s_.xml' % sequence_name)

#     def run_beast(self, tolerance):
#         beast_xml = 'BEAST_XML_%s.xml' % identifier
#         BEAST = 'java -jar %s %s -prefix %s -beagle -seed %s' % (path_to_beast,
#                 beast_xml, identifier, str(randrange(0, 999999)))
#         subprocess.call(BEAST.split())
#         if tolerance == True:
#             resume_beast('NAME OF BEAST LOG FILE')

#     def resume_beast(self, BEAST_log_file):
#         ToleranceCheck(BEAST_log_file)
#         BEAST_log_file.calculate_statistics()
#         for i in st_dev:
#             if i > tolerance:
#                 BEAST = 'java -jar %s %s -prefix %s -beagle -seed %s -resume' % (path_to_beast, beast_xml, identifier, str(randrange(0, 999999)))

class IterRegistry(type):

    """A metaclass to allow for iteration over instances of NexusFile class."""

    def __iter__(cls):
        return iter(cls.registry)

class NexusFile(Garli):

    """A class in which we will store the name and unique associated with the
       given nexus file."""

    __metaclass__ = IterRegistry
    registry = []

    def __init__(self, seq_name, path, seq_file):
        self.path = str(path)
        self.sequence_name = self.path.strip('.nex')
        self.nexus_file = seq_file.readlines()
        self.identifier = str(seq_name) + '_' + str(randrange(0, 999999999))
        self.JMT_ID = 'jModelTest_%s.out' % self.identifier
        self.parameters = {}
        self.BEAST_ID = 'BEAST_%s.out' % self.identifier
        self.registry.append(self)

script, batch, tolerance, path_to_jModelTest, path_to_beast = argv

path_to_sequence = {}

if batch == 'True':
    cwd = os.getcwd()
    files_in_dir = os.listdir(cwd)
    nexus_files = filter(lambda x: '.nex' in x, files_in_dir)
    for i in nexus_files:
        path = i
        class_name = i.strip('.nex')
        path_to_sequence[str(class_name)] = str(path)
else:
    print ('The program will prompt you for the path to each sequence file ' + 
           'as well as a unique name for each instantiated class.')
    no_runs = raw_input('How many runs would you like to perform? ')
    for i in range(int(no_runs)):
        path = raw_input('Path to sequence: ')
        class_name = raw_input('Name of class: ')
        path_to_sequence[str(class_name)] = str(path)

no_bootstrapreps = raw_input('How many bootstrap replications would you ' + 
                             'like to perform in the garli run? ')
# chain_length = raw_input('How long would you like to run the MCMC chain in ' +
#                         'the BEAST run? ')
# store_every = raw_input('How often would you like the chain to sample in ' +
#                         'the BEAST run? By default, the burnin is set to ' +
#                         'a quarter of samples.')
# burnin = (int(chain_length) / int(store_every)) * 0.25

for key in path_to_sequence:
     with open(str(path_to_sequence[key]), 'r') as sequence_file:
         key = NexusFile(key, path_to_sequence[key], sequence_file)

for sequence in NexusFile:
    print '------------------------------------------------------------------'
    print 'Sequence file: %s' % sequence.sequence_name
    print 'Run identifier: %s' % sequence.identifier
    print '------------------------------------------------------------------'
    sequence.run_jModelTest()
    with open(str(sequence.JMT_ID), 'r') as JMT_output:
        JMT_output = JMT_output.readlines()
        sequence.r_jModelTest_parameters(JMT_output)
        print sequence.parameters
    # with open('garli.conf', 'r+') as garli_conf:
    #     garli_conf = garli_conf.readlines()
    #     sequence.w_garli_conf(garli_conf)
    #     sequence.run_garli()
    # with open('Standard.xml', 'r+') as BEAST_xml:
    #     BEAST_xml = BEAST_xml.readlines()
    #     sequence.w_beast_xml(BEAST_xml)
    #     sequence.run_beast()