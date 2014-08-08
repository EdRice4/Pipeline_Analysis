from random import randrange

class DefineRange(object):

    """Returns the range of user specified start and end sequences."""

    def get_range(self, range_file, start, end):
        range_start = range_file.index(start)
        range_file = range_file[range_start:]
        range_end = range_file.index(end) + range_start
        return range_start, range_end

class NexusFile(DefineRange):

    """A class in which we will store the name and unique associated with the
       given nexus file."""

    def __init__(self, seq_file):
        self.seq_file = seq_file.readlines()
        self.path = str(seq_file)
        self.sequence_name = self.path.rpartition("/")[-1]
        self.identifier = (str(self.sequence_name) + '_' + 
                           str(randrange(0, 999999999)))

    def identify_taxon_and_seq(seq_file):
        sequence_start, sequence_end = get_range(self, self.seq_file, 
                                                 '\tmatrix\n', '\n')
        sequence_start += 1
        for line in seq_file:
            while sequence_start <= sequence_end:
                species_id = getline(str(path_to_sequence), int(sequence_start)).rpartition("\t")[0]
                species_sequence = getline(str(path_to_sequence), int(sequence_start)).rpartition("\t")[-1]
                data = root.find('data')
                sequence = ET.Element('sequence', id='%s' % species_id, taxon='%s' % species_id, totalcount='4', value='%s' % species_sequence)
                data.append(sequence)
                output.write('Standard_%s_.xml' % identifier)

with open('Cerapachys_ULTIMATE_NOTRM_UNDERSCORE.nex', 'r') as seq_file:
    Cerapachys = NexusFile(seq_file)
    
print Cerapachys.get_range(Cerapachys.seq_file, '\tmatrix\n', '\n')