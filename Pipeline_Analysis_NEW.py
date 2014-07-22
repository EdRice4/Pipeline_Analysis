#!/usr/bin/python

# Import modules.
import os
from shutil import copy, move, make_archive
import subprocess
import linecache
import xml.etree.ElementTree as ET
from random import randrange

# Will need this later to read output of jModelTest.
def r_jModelTest_model(jModelTest_file):
    for line in jModelTest_file:
        if 'Model = ' in line:
            model_selected = line.rpartition(' ')[-1]
    return model_selected

# Will need this later to read output of jModelTest
def r_jModelTest_parameters(jModelTest_file):
    for line in jModelTest_file:
        if 'freqA' in line:
            freqA = line.rpartition(' ')[-1]
        if 'freqC' in line:
            freqC = line.rpartition(' ')[-1]
        if 'freqG' in line:
            freqG = line.rpartition(' ')[-1]
        if 'freqT' in line:
            freqT = line.rpartition(' ')[-1]
        if 'R(a) [AC]' in line:
            Ra = line.rpartition(' ')[-1]
        if 'R(b)' in line:
            Rb = line.rpartition(' ')[-1]
        if 'R(c)' in line:
            Rc = line.rpartition(' ')[-1]
        if 'R(d)' in line:
            Rd = line.rpartition(' ')[-1]
        if 'R(e)' in line:
            Re = line.rpartition(' ')[-1]
        if 'R(f)' in line:
            Rf = line.rpartition(' ')[-1]

# Will need this later to read and write garli.conf file.
def w_garli_conf(garli_file):
    configuration = garli_conf.readlines()
    model_selected = r_jModelTest_model(garli_file)
    for i,value in enumerate(configuration):
        if value.find('datafname') != -1:
             configuration[i] = 'datafname = %s\n' % output_id
        if value.find('ofprefix') != -1:
            configuration[i] = 'ofprefix = %s\n' % identifier
        if value.find('bootstrapreps') != -1:
            configuration[i] = 'bootstrapreps = %s\n' % no_bootstrapreps
        if value.find('datatype') != -1:
            configuration('datatype = nucleotide\n')
        if value.find('ratematrix') != -1:
            configuration[i] = 'ratematrix = %s\n' % all_possible_models[str(model_selected)][0]
        if value.find('statefrequencies') != -1:
            configuration[i] = 'statefrequencies = %s\n' % all_possible_models[str(model_selected)][1]
        if value.find('ratehetmodel') != -1:
            if '+G' in str(model_selected):
                configuration[i] = 'ratehetmodel = gamma\n'
            else:
                configuration[i] = 'ratehetmodel = none\n'
        if value.find('numratecats') != -1:
            if '+G' in str(model_selected):
                configuration[i] = 'numratecats = 4\n'
            else:
                configuration[i] = 'numratecats = 1\n'
        if value.find('invariantsites') != -1:
            if '+I' in str(model_selected):
                configuration[i] = 'invariantsites = estimate\n'
            else:
                configuration[i] = 'invariantsites = none\n'
    output.write(str(configuration))

# Will need this later to provide boundaries on sequences in nexus file.
def get_range(seq_file):
    sequence_start = 0
    sequence_end = 0
    for num,line in enumerate(sequence_file, start=1):
        if 'matrix' in line.lower():
            sequence_start = num
        if line == '\n':
            sequence_end = num
    return sequence_start, sequence_end

# Will need this later to read sequences in nexus file and write to XML file.
def identify_taxon_and_seq(seq_file):
    seq_file = seq_file.readlines()
    sequence_start, sequence_end = get_range(seq_file)
    sequence_start += 1
    for line in seq_file:
        while sequence_start <= sequence_end:
                species_id = linecache.getline(str(path_to_sequence), int(sequence_start)).rpartition("\t")[0]
                species_sequence = linecache.getline(str(path_to_sequence), int(sequence_start)).rpartition("\t")[-1]
                data = root.find('data')
                sequence = ET.Element('sequence', id='%s' % species_id, taxon='%s' % species_id, totalcount='4', value='%s' % species_sequence)
                data.append(sequence)
                output.write('Standard_%s_.xml' % identifier)

# Will need this later to replce values in XML value with desired values.
def replace_values_xml(xml_file):

# Define models for reference.
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

# Ensure you are in home dir.
home_dir = os.path.expanduser('~')
while os.getcwd() != home_dir:
    os.chdir(home_dir)

# User input to find sequence file and jModelTest, respectively.
path_to_sequence = raw_input('Path to sequence file: ')
path_to_jModelTest = raw_input('Path to jModelTest.jar: ')

# Generate random identifier tag for run.
sequence_name = path_to_sequence.rpartition("/")[-1]
identifier = str(sequence_name) + '_' + str(randrange(0, 999999999))

# Run jModelTest and create output file, jModelTest.out.
jModelTest = 'java -jar %s -d %s -t fixed -o jModelTest_%s_.out -s 11 -i -g 4 -f -tr 1' % (path_to_jModelTest, path_to_sequence, identifier)
subprocess.call(jModelTest.split())

# Molecular clock test?

# Write to garli.conf file.
no_bootstrapreps = raw_input('How many bootstrap replications would you like to perform? ')
with open('garli.conf', 'r+') as garli_conf:
    output = open("garli_%s_.conf" % identifier, 'w')
    w_garli_conf(garli_conf)
    while output.closed != True:
        output.close()

# Run garli; best to put garli in /usr/local/bin.
subprocess.call('garli')

# Prepare BEAST XML file for desired run.

# Read sequence file and write to BEAST XML file.
with open(str(path_to_sequence), 'r') as seq_file:
    output = ET.parse('Standard.xml')
    root = output.getroot()
    identify_taxon_and_seq(seq_file)
    while seq_file.closed != True:
        seq_file.close()

# Copy and rename sequence file then clean up folder, creating directory and archive of latest run.
move("*" + str(identifier) + "*", str(identifier))
copy(str(path_to_sequence), str(identifier))
os.chdir(str(identifier))
os.rename(str(sequence_name), str(identifier))
os.chdir("..")
archive_name = os.path.expanduser(os.path.join('~', str(identifier)))
root_dir = os.path.expanduser(os.path.join('~', str(identifier)))
make_archive(archive_name, 'gztar', root_dir)