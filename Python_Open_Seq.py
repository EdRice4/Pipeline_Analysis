import linecache

path_to_sequence = raw_input("Path to sequence file: ")

# sequence_start = 0
# sequence_end = 0

def get_range(seq_file):
    # global sequence_start
    # global sequence_end
    sequence_start = 0
    sequence_end = 0
    for num,line in enumerate(seq_file, start=1):
        if "matrix" in line.lower():
            sequence_start = num
            # return sequence_start
        if line == "\n":
            sequence_end = num
            # return sequence_end
    return sequence_start, sequence_end
    # return sequence_end
    # print sequence_start
    # print sequence_end

def identify_taxon_and_seq(seq_file):
    sequence_start, sequence_end = get_range(seq_file)
    sequence_start += 1
    # within = range(sequence_start, sequence_end)
    # return within
    # current_line = int(sequence_start) + iterator
    for line in seq_file:
        while sequence_start <= sequence_end:
            # for num,line in enumerate(seq_file, start=1):
            # return line
                species_id = linecache.getline(str(path_to_sequence), int(sequence_start)).rpartition("\t")[0]
                output.write(str(species_id) + "\n")
                species_sequence = linecache.getline(str(path_to_sequence), int(sequence_start)).rpartition("\t")[-1]
                output.write(str(species_sequence) + "\n")
                # if num in within:
            # species_id = linecache.getline(str(path_to_sequence), int(current_line)),rpartition(" ")[0]
                # if num in within:
                # return num, line
                sequence_start += 1
                # return sequence_start
        # return species_id
            # if num in within:            
                    # species_id = linecache.getline(str(path_to_sequence), int(sequence_start) + 1)
                    # species_id = species_id.rpartition(" ")[0]
                    # return species_id
                    # sequence_start += 1
                # sequence_file.write("%s" % species_id)
                # species_sequence = linecache.getline(str(path_to_sequence), int(sequence_start) + int(iterator)).rpartition(" ")[0]
                # return species_sequence 
                # sequence_file.write("%s" % species_sequence)
                # iterator += 1

with open(str(path_to_sequence), "r") as seq_file:
    sequence_file = seq_file.readlines()
    output = open("output.txt", "w")
    print identify_taxon_and_seq(sequence_file)
while seq_file.closed != True:
    seq_file.close()
while output.closed != True:
    output.close()
    # sequence_start = 0
    # sequence_end = 0


# print sequence_start
# print sequence_end
    # print sequence_start, sequence_end