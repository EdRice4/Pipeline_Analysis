all_possible_models = {
    "JC" : ["1rate", "equal"],
    "F81" : ["1rate", "estimate"],
    "K80" : ["2rate", "equal"],
    "HKY" : ["2rate", "estimate"],
    "trNef" : ["0 1 0 0 2 0", "equal"],
    "TrN" : ["0 1 0 0 2 0", "estimate"],
    "K81" : ["0 1 2 2 1 0", "equal"],
    "K3Puf" : ["0 1 2 2 1 0", "estimate"],
    "TIMef" : ["0 1 2 2 3 0", "equal"],
    "TIM" : ["0 1 2 2 3 0", "estimate"],
    "TVMef" : ["0 1 2 3 1 4", "equal"],
    "TVM" : ["0 1 2 3 1 4", "estimate"],
    "SYM" : ["6rate", "equal"],
    "GTR" : ["6rate", "estimate"]
}

ofprefix = raw_input("What would you like ths run to be called? ")

model_selected = {"TIM+I+G" : ["6rate", "estimated"]}

with open("garli.conf", "r+") as garli_conf:
    for line in garli_conf:
        if "dataframe" in line:
            garli_conf.write("dataframe = sequence_file")
        if "ofprefix" in line:
            garli_conf.write("ofprefix = %s" % ofprefix)
        if "bootstrapreps" in line:
            garli_conf.write("bootstrapreps = 1000")
        if "datatype" in line and "+I" in str(model_selected):
            garli_conf.write("datatype = nucleotide")
        if "ratematrix" in line:
            garli_conf.write("ratematrix = %s" % all_possible_models[str(model_selected)][0])
        if "statefrequencies" in line:
        	garli_conf.write("statefrequencies = %s" % all_possible_models[str(model_selected)][1])
        if "ratehetmodel" in line:
            if "+G" in str(model_selected):
                garli_conf.write("ratehetmodel = gamma")
            else:
                garli_conf.write("ratehetmodel = none")