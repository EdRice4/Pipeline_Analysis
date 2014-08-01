with open('jModelTest_rodents.nex.out', 'r') as jModelTest_file:
    jModelTest_file = jModelTest_file.readlines()
    print jModelTest_file.index(' Model selected: \n')