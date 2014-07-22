import linecache
import xml.etree.ElementTree as ET

path_to_sequence = raw_input("Path to sequence file: ")

def get_range(seq_file):
    sequence_start = 0
    sequence_end = 0
    for num,line in enumerate(seq_file, start=1):
        if "matrix" in line.lower():
            sequence_start = num
        if line == "\n":
            sequence_end = num
    return sequence_start, sequence_end

# Will need this later to read sequences in nexus file.
def identify_taxon_and_seq(seq_file):
    seq_file = seq_file.readlines()
    sequence_start, sequence_end = get_range(seq_file)
    sequence_start += 1
    for line in seq_file:
        while sequence_start <= sequence_end:
                species_id = linecache.getline(str(path_to_sequence), int(sequence_start)).rpartition("\t")[0]
                species_sequence = linecache.getline(str(path_to_sequence), int(sequence_start)).rpartition("\t")[-1]
                data = ET.Element('data', id='%s' % species_id name='alignment')
                sequence = ET.Element('sequence', id='%s' % species_id, taxon='%s' % species_id, totalcount='4', value='%s' % species_sequence)
                data.append(sequence)
                output.write('Standard.xml')
                # output.write(str(species_sequence) + "\n")
                sequence_start += 1

with open(str(path_to_sequence), 'r') as seq_file:
    output = ET.parse('Standard.xml')
    root = output.getroot()
    identify_taxon_and_seq(seq_file)
    while seq_file.closed != True:
        seq_file.close()
    # while output.closed != True:
        # output.close()