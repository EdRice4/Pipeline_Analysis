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
        for num, i in enumerate(range_file):
            range_start = range_file.index(start)
            range_file = range_file[range_start:]
            range_end = range_file.index(end) + range_start
        return range_start, range_end

    def filter_output(output, start, end):
        output = output[start:end]
        for num, i in enumerate(output):
            output[num] = i.translate(None, ' \n')

class IterRegistry(type):

    """A metaclass to allow for iteration over instances of NexusFile class."""

    def __iter__(cls):
        return iter(cls.registry)

class jModelTest(FileMethods):

    """Run jModelTest and store parameters associated with output."""

    def run_jModelTest(self):
        jModelTest = 'java -jar %s -d %s -t fixed -o %s. -s 11 -i -g 4 -f -tr 1' % (path_to_jModelTest, 
                                                     self.sequence_name,
                                                     self.JMT_ID)
        call(jModelTest.split())

    def r_jModelTest_parameters(self, jModelTest_file):
        start, end = self.get_range(jModelTest_file, ' Model selected: \r\n', ' \r\n')
        data = filter_output(jModelTest_file, start + 1, end)
        parameters = []
        for i in data:
            parameter = i.rpartition('=')[0]
            value = i.rpartition('=')[-1]
            parameters.append([parameter, value])
        return parameters

class NexusFile(jModelTest):

    """A class in which we will store the name and unique associated with the
       given nexus file."""

    __metaclass__ = IterRegistry
    registry = []

    def __init__(self, seq_name, path, seq_file):
        self.identifier = str(seq_name) + '_' + str(randrange(0, 999999999))
        self.sequence_name = str(path)
        self.JMT_ID = 'jModelTest_%s.out' % self.identifier
        # BEASY ID
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

script, batch, path_to_jModelTest, path_to_beast, tolerance = argv

path_to_sequence = {}

if bool(batch) == True:
    print ('The program will prompt you for the path to each sequence file ' + 
           'as well as a unique name for each instantiated class.')
    no_runs = raw_input('How many runs would you like to perform? ')
    for i in range(int(no_runs)):
        path = raw_input('Path to sequence: ')
        class_name = raw_input('Name of class: ')
        path_to_sequence[str(class_name)] = str(path)
else:
    print ('The program will prompt you for the path to the sequence file ' +
           'as well as a name for the instantiated class.')
    path = raw_input('Path to sequence: ')
    class_name = raw_input('Name of class: ')
    path_to_sequence[str(class_name)] = str(path)

for key in path_to_sequence:
     with open(str(path_to_sequence[key]), 'r') as sequence_file:
         key = NexusFile(key, path_to_sequence[key], sequence_file)

for sequence in NexusFile:
    print sequence.identifier
    print sequence.sequence_name
    sequence.run_jModelTest()
    with open(str(sequence.JMT_ID), 'r') as JMT_output:
        JMT_output = JMT_output.readlines()
        print sequence.r_jModelTest_parameters(JMT_output)