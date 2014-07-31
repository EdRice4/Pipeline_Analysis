with open('jModelTest_rodents.nex.out') as jModelTest_file:

    def contains(item, iterable):
        matching = []
        for x in item:
            matching.extend(i for i in iterable if x in i)
        return matching

    def r_jModelTest_parameters(jModelTest_file):
        search = ['freqA', 'freqC', 'freqG', 'freqT', 'R(a)', 'R(b)', 'R(c)',
                  'R(d)', 'R(e)', 'R(f)', 'p-inv', 'gamma shape']
        jModelTest_file = jModelTest_file.readlines()
        jModelTest_file = filter(lambda x: )
        # for parameter in search: 
        #     matching = [i for num, i in enumerate(jModelTest_file) if contains(parameter, jModelTest_file) == True and num > model]
        # return matching
        # for i in zip(jModelTest_file, search):
        #     return filter(lambda x: str(search) in str(jModelTest_file), jModelTest_file)
        # for i in search:
        #     if i in jModelTest_file:
        #         return i
    #         search[num] in jModelTest_file[num]:
    #             return item
    print r_jModelTest_parameters(jModelTest_file)
    #     if 'freqA' in line:
    #         freqA = line.rpartition(' ')[-1]
    #     if 'freqC' in line:
    #         freqC = line.rpartition(' ')[-1]
    #     if 'freqG' in line:
    #         freqG = line.rpartition(' ')[-1]
    #     if 'freqT' in line:
    #         freqT = line.rpartition(' ')[-1]
    #     if 'R(a) [AC]' in line:
    #         Ra = line.rpartition(' ')[-1]
    #     if 'R(b)' in line:
    #         Rb = line.rpartition(' ')[-1]
    #     if 'R(c)' in line:
    #         Rc = line.rpartition(' ')[-1]
    #     if 'R(d)' in line:
    #         Rd = line.rpartition(' ')[-1]
    #     if 'R(e)' in line:
    #         Re = line.rpartition(' ')[-1]
    #     if 'R(f)' in line:
    #         Rf = line.rpartition(' ')[-1]
    #     if "p-inv" in line:
    #         p_inv = line.rpartition(' ')[-1]
    #     if 'gamma shape' in line:
    #         gamma_shape = line.rpartition(' ')[-1]
    # parameters.append(freqA)
    # parameters.append(freqC)
    # parameters.append(freqG)
    # parameters.append(freqT)
    # parameters.append(Ra)
    # parameters.append(Rb)
    # parameters.append(Rc)
    # parameters.append(Rd)
    # parameters.append(Re)
    # parameters.append(Rf)
    # parameters.append(p_inv)
    # parameters.append(gamma_shape)
    # for num,item in enumerate(parameters):
    #     item = item.replace('\n', '')
    #     parameters[num] = item
    # return parameters