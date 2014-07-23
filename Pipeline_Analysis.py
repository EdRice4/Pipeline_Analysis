#!/usr/bin/python

# Import modules.
import os
from shutil import copy, move, make_archive
import subprocess
import linecache
from lxml import etree as ET
from random import randrange

# Will need this later to read output of jModelTest.
def r_jModelTest_model(jModelTest_file):
    for line in jModelTest_file:
        if 'Model = ' in line:
            model_selected = line.rpartition(' ')[-1]
    return model_selected.replace('\n', '')

# Will need this later to read output of jModelTest
def r_jModelTest_parameters(jModelTest_file):
    parameters = []
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
        if 'gamma shape' in line:
            gamma_shape = line.rpartition(' ')[-1]
    parameters.append(freqA)
    parameters.append(freqC)
    parameters.append(freqG)
    parameters.append(freqT)
    parameters.append(Ra)
    parameters.append(Rb)
    parameters.append(Rc)
    parameters.append(Rd)
    parameters.append(Re)
    parameters.append(Rf)
    parameters.append(gamma_shape)
    for num,item in enumerate(parameters):
        item = item.replace('\n', '')
        parameters[num] = item
    return parameters

# Will need this later to read and write garli.conf file.
# Better to provide pInv?
# Run multiple threaded version?
def w_garli_conf(garli_file):
    configuration = garli_conf.readlines()
    model_selected = r_jModelTest_model(garli_file)
    no_bootstrapreps = raw_input('How many bootstrap replications would you like to perform? ')
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

# Will need this later to replce values in XML value with desired values.
def w_beast_xml(xml_file):
    taxon_name = sequence_name.replace('.nex', '')
    beast_xml = xml_file.readlines()
    for num,item in enumerate(beast_xml):
        item = item.replace('PUT_NAME_OF_FILE_SANS_NEX_HERE', str(taxon_name))
        beast_xml[num] = item
    beast_xml = ''.join(beast_xml)
    beast_xml = ET.XML(beast_xml)
    output.write(ET.tostring(beast_xml, pretty_print=True))

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

# Ensure you are in home dir; if all files are dumped in one directory, easy to clean and organize.
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
with open('garli.conf', 'r+') as garli_conf:
    output = open("garli_%s_.conf" % identifier, 'w')
    w_garli_conf(garli_conf)
    while output.closed != True:
        output.close()

# Run garli; best to put garli in /usr/local/bin.
subprocess.call('garli')

# Prepare BEAST XML file for desired run.
with open('Standard.xml', 'r+') as beast_xml:
    output = open('BEAST_XML_%s.xml' % identifier, 'w')
    w_beast_xml(beast_xml)
    while output.closed != True:
        output.close()

# Read sequence file and write to BEAST XML file.
with open(str(path_to_sequence), 'r') as seq_file:
    output = ET.parse('Standard.xml')
    root = output.getroot()
    identify_taxon_and_seq(seq_file)
    while seq_file.closed != True:
        seq_file.close()

# Copy and rename sequence file then clean up folder, creating directory and archive of latest run.
clean_up()