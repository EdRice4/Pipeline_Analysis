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

print all_possible_models["TrN"][1]