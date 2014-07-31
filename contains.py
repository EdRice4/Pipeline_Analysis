with open('jModelTest_rodents.nex.out') as jModelTest_file:
    search = ['freqA', 'freqC', 'freqG', 'freqT', 'R(a)', 'R(b)', 'R(c)', 'R(d)', 'R(e)', 'R(f)', 'p-inv', 'gamma shape']
    jModelTest_file = jModelTest_file.readlines()

    def contains(item, iterable):
        matching = []
        for x in item:
            matching.extend(i for i in iterable if x in i)
        return matching

        # model = [num for num, i in enumerate(jModelTest_file) if 'Model selected:' in i]
        # matching = [i for num, i in enumerate(jModelTest_file) if contains(i, search) == True] # and int(num) > model[0]]
        # return matching

    # for parameter in search:
    #     matching = [i for i in jModelTest_file if contains(parameter, i) == True]

    print contains('freqC', search)