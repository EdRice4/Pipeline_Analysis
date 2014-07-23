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

with open("jModelTest_rodents.nex.out", "r") as jModelTest_file:
    freqA, freqC, freqG, freqT, Ra, Rb, Rc, Rd, Re, Rf, gamma_shape = r_jModelTest_parameters(jModelTest_file)
    print freqA