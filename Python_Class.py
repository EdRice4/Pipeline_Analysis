from sys import argv
from random import randrange

class DefineRange(object):

    """Returns the range of user specified start and end sequences."""

    def get_range(self, range_file, start, end):
        range_start = range_file.index(start)
        range_file = range_file[range_start:]
        range_end = range_file.index(end) + range_start
        return range_start, range_end

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
        sequence_start, sequence_end = get_range(self, self.nexus_file, 
                                                 '\tmatrix\n', '\n')
        sequence_start += 1
        seq_file = seq_file.readlines()
        for line in seq_file:
            while sequence_start <= sequence_end:
                species_id = getline(str(path_to_sequence), int(sequence_start)).rpartition("\t")[0]
                species_sequence = getline(str(path_to_sequence), int(sequence_start)).rpartition("\t")[-1]
                data = root.find('data')
                sequence = ET.Element('sequence', id='%s' % species_id, taxon='%s' % species_id, totalcount='4', value='%s' % species_sequence)
                data.append(sequence)
                output.write('Standard_%s_.xml' % identifier)

script, batch = argv

path_to_sequence = {}

if batch == 'True':
    print ('The program will prompt you for the path to each sequence file ' + 
           'as well as a unique name for each instantiated class.')
    no_runs = raw_input('How many runs would you like to perform? ')
    for i in range(int(no_runs)):
        path = raw_input('Path to sequence: ')
        class_name = raw_input('Name of class: ')
        path_to_sequence[str(class_name)] = str(path)
else:
    print ('The program will prompt you for the path to the sequence file as ' +
           'well as a name for the instantiated class.')
    path = raw_input('Path to sequence: ')
    class_name = raw_input('Name of class: ')
    path_to_sequence[str(class_name)] = str(path)

for key in path_to_sequence:
    with open(str(path_to_sequence[key]), 'r') as sequence_file:
        key = NexusFile(key, sequence_file)

for nexusobject in NexusFile:
    print nexusobject.get_range(nexusobject.nexus_file, '\tmatrix\n', '\n')