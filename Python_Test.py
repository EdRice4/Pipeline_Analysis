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
        for num, i in enumerate(range_file):
            range_file[num] = i.lower()
        range_start = range_file.index(start)
        range_file = range_file[range_start:]
        range_end = range_file.index(end) + range_start
        return range_start, range_end

    def filter_output(output, start, end):
        output = output[start:end]
        for num, i in enumerate(output):
            output[num] = i.translate(None, ' \n')
        return output

class ToleranceCheck(object):

    """A class that can calculate statistics of data in a file separated into
       columns."""

    def __init__(self, data_file):
        data = [line.split() for line in self.data_file if isinstance(line[:1], num) == True]
        cat_data = zip(*data)

    def calculate_statistics(data):
        st_dev = []
        for i in data:
            parameter = i[0]
            data = array(i[1:])
            st_dev.append([parameter, std(i)])
        return st_dev

class IterRegistry(type):

    """A metaclass to allow for iteration over instances of NexusFile class."""

    def __iter__(cls):
        return iter(cls.registry)

class NexusFile(DefineRange):

    """A class in which we will store the name and unique associated with the
       given nexus file."""

    __metaclass__ = IterRegistry
    registry = []

    def __init__(self, seq_name, seq_file):
        self.sequence_name = str(seq_name) + '_' + str(randrange(0, 999999999))
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
                output.write('Standard_%s_.xml' % identifier)

class jModelTest(GetRange):

    """Run jModelTest and store parameters associated with output."""

    def run_jModelTest():
        jModelTest = ('java -jar %s -d %s -t fixed -o jModelTest_%s_.out' + 
                      '-s 11 + -i -g 4 -f -tr 1') % (path_to_jModelTest, 
                                                   path_to_sequence, identifier)
        call(jModelTest.split())

    def r_jModelTest_parameters(jModelTest_file):
        start, end = get_range(output, ' Model selected: \n', ' \n')
        data = filter_output(jModelTest_file, start + 1, end)
        parameters = []
        for i in data:
            parameter = i.rpartition('=')[0]
            value = i.rpartition('=')[-1]
            parameters.append([parameter, value])
        return parameters

class Garli(DefineIndices):

    """Run garli and store parameters associated with output."""

    def __init__(self, input_file):
        self.garli_conf = input_file.readlines()

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
            'TMef' : ['0 1 2 2 3 0', 'equal'], # Remove 'I' for translate.
            'TM' : ['0 1 2 2 3 0', 'estimate'], # Remove 'I' for translate.
            'TVMef' : ['0 1 2 3 1 4', 'equal'],
            'TVM' : ['0 1 2 3 1 4', 'estimate'],
            'SYM' : ['6rate', 'equal'],
            'GTR' : ['6rate', 'estimate']
        }

        configuration = garli_conf.readlines()
        model_selected = r_jModelTest_model(jModelTest_file)[0][1]
        model_selected = model_selected.translate(None, '+IG')
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

    def run_garli():
        garli = 'garli'
        garli_run = Popen(garli, stderr = STDOUT, stdout = PIPE)
        garli_out, garli_err = garli_run.communicate()
        return garli_out

class BEAST(object):

    """Run BEAST and store parameters associated with output."""

    def w_beast_xml(jModelTest_file, xml_file):
        (freqA, freqC, freqG, freqT, Ra, Rb, Rc, Rd, Re, Rf, gamma_shape, p-inv 
         = r_jModelTest_parameters(jModelTest_file))
        chain_length = raw_input("How long would you like to run the chain? ") # Make this standard.
        store_every = raw_input("How often would you like the chain to sample? ") # Make this standard.
        taxon_name = sequence_name.strip('.nex')
        beast_xml = xml_file.readlines()
        for num,item in enumerate(beast_xml):
            item = item.replace('PUT_NAME_OF_FILE_SANS_NEX_HERE', str(taxon_name))
            beast_xml[num] = item
        beast_xml = ET.XML((''.join(beast_xml)))
        output.write(ET.tostring(beast_xml, pretty_print = True))

    def run_beast(tolerance):
        beast_xml = 'BEAST_XML_%s.xml' % identifier
        BEAST = 'java -jar %s %s -prefix %s -beagle -seed %s' % (path_to_beast,
                beast_xml, identifier, str(randrange(0, 999999)))
        subprocess.call(BEAST.split())
        if tolerance == True:
            resume_beast('NAME OF BEAST LOG FILE')

    def resume_beast(BEAST_log_file):
        ToleranceCheck(BEAST_log_file)
        BEAST_log_file.calculate_statistics()
        for i in st_dev:
            if i > tolerance:
                BEAST = 'java -jar %s %s -prefix %s -beagle -seed %s -resume'
                        % (path_to_beast, beast_xml, identifier, 
                           str(randrange(0, 999999)))

class CleanUp(object):

    """Clean up directory, i.e., move all output from run to unique directory
       and make archive of directory."""

    def clean_up():
        move("*" + str(identifier) + "*", str(identifier))
        copy(str(path_to_sequence), str(identifier))
        os.chdir(str(identifier))
        os.rename(str(sequence_name), str(identifier))
        os.chdir("..")
        archive_name = os.path.expanduser(os.path.join('~', str(identifier)))
        root_dir = os.path.expanduser(os.path.join('~', str(identifier)))
        make_archive(archive_name, 'gztar', root_dir)

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
        key = NexusFile(key, sequence_file)

for sequence in NexusFile:
    print sequence.identifier