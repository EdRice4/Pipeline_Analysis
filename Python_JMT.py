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
            output[num] = i.translate(None, ' \r\n')
        return output

class IterRegistry(type):

    """A metaclass to allow for iteration over instances of NexusFile class."""

    def __iter__(cls):
        return iter(cls.registry)

class jModelTest(FileMethods):

    """Run jModelTest and store parameters associated with output."""

    def run_jModelTest(self):
        jModelTest = 'java -jar %s -d %s -t fixed -s 11 -i -g 4 -f -tr 1' % (path_to_jModelTest, self.sequence_name)
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
        return parameters

class Garli(jModelTest):

    """Run garli and store parameters associated with output."""

    def __init__(self, input_file):
        self.garli_conf = input_file.readlines()

    def w_garli_conf(self, jModelTest_params, garli_file):

        all_possible_models = {
            'JC' : ['1rate', 'equal'],
            'F81' : ['1rate', 'estimate'],
            'K80' : ['2rate', 'equal'],
            'HKY' : ['2rate', 'estimate'],
            'trNef' : ['0 1 0 0 2 0', 'equal'],
            'TrN' : ['0 1 0 0 2 0', 'estimate'],
            'K81' : ['0 1 2 2 1 0', 'equal'],
            'K3Puf' : ['0 1 2 2 1 0', 'estimate'],
            'TMef' : ['0 1 2 2 3 0', 'equal'], # Remove 'I' for translate.
            'TM' : ['0 1 2 2 3 0', 'estimate'], # Remove 'I' for translate.
            'TVMef' : ['0 1 2 3 1 4', 'equal'],
            'TVM' : ['0 1 2 3 1 4', 'estimate'],
            'SYM' : ['6rate', 'equal'],
            'GTR' : ['6rate', 'estimate']
        }

        model_selected = jModelTest_params[0][1]
        het = '+G' in model_selected
        inv = '+I' in model_selected
        model_selected = model_selected.translate(None, '+IG')
        no_bootstrapreps = raw_input('How many bootstrap replications would' +
                                     ' you like to perform? ')
        for num,item in enumerate(garli_file):
            if item.find('datafname') != -1:
                item = 'datafname = %s\n' % self.sequence_name
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
                item = 'ratematrix = %s\n' % all_possible_models[str(model_selected)][0]
                garli_file[num] = item
            if item.find('statefrequencies') != -1:
                item = 'statefrequencies = %s\n' % all_possible_models[str(model_selected)][1]
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

class NexusFile(Garli):

    """A class in which we will store the name and unique associated with the
       given nexus file."""

    __metaclass__ = IterRegistry
    registry = []

    def __init__(self, seq_name, path, seq_file):
        self.identifier = str(seq_name) + '_' + str(randrange(0, 999999999))
        self.sequence_name = str(path)
        self.JMT_ID = 'jModelTest_%s.out' % self.identifier
        # BEAST ID
        self.nexus_file = seq_file.readlines()
        self.registry.append(self)

    def identify_taxon_and_seq(seq_file):
        sequence_start, sequence_end = get_range(self, self.seq_file, '\tmatrix\n',
                                                 '\n')
        sequence_start += 1
        seq_file = seq_file.readlines()
        for line in seq_file:
            while sequence_start <= sequence_end:
                species_id = getline(str(path_to_sequence), int(sequence_start)).rpartition("\t")[0]
                species_sequence = getline(str(path_to_sequence), int(sequence_start)).rpartition("\t")[-1]
                data = root.find('data')
                sequence = ET.Element('sequence', id='%s' % species_id,
                                      taxon='%s' % species_id, totalcount='4',
                                      value='%s' % species_sequence)
                data.append(sequence)
                output.write('Standard_%s_.xml' % sequence_name)

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
        jModelTest_params = sequence.r_jModelTest_parameters(JMT_output)
    with open('garli.conf', 'r+') as garli_conf:
        garli_conf = garli_conf.readlines()
        sequence.w_garli_conf(jModelTest_params, garli_conf)
        sequence.run_garli()