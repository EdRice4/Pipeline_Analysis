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
        if 'gamma shape' in line:
            gamma_shape = line.rpartition(' ')[-1]
    return freqA, freqC, freqG, freqT, Ra, Rb, Rc, Rd, Re, Rf, gamma_shape

with open("jModelTest_rodents.nex.out", "r") as jModelTest_file:
    print r_jModelTest_parameters(jModelTest_file)