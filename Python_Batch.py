path_to_sequence = []
no_runs = raw_input('How many runs would you like to perform? The program ' +
                    'will prompt you for the path to each sequence file.\n>')
for i in range(int(no_runs)):
    path_to_sequence.append(raw_input('Path to sequence: '))
print path_to_sequence