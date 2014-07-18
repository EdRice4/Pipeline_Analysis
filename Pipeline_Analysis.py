#!/usr/bin/python

import os
import subprocess

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
                        

# Ensure you are in directory where you want jModelTest output to be saved.
if os.getcwd() != "/home/lab":
    os.chdir("/home/lab")

# User input to find sequence file and jModelTest, respectively.
path_to_sequence = raw_input("Path to sequence file: ")
path_to_jModelTest = raw_input("Path to jModelTest.jar: ")

# Set variable to name output files, this distinguishing between runs.
sequence_file = path_to_sequence.rpartition("/")[-1]

# Run jModelTest and create output file, jModelTest.out, in jModelTest directory.
jModelTest = "java -jar %s -d %s -t fixed -o jModelTest_%s_.out -s 11 -i -g 4 -f -tr 1" % (path_to_jModelTest, path_to_sequence, sequence_file)
subprocess.call(jModelTest.split())

# Open jModelTest.out in read-only mode and obtain selected model.
with open(str(os.getcwd()) + "/jModelTest_%s_.out" % sequence_file, "r") as jModelTest_output:
    for line in jModelTest_output:
        if "Model = " in line:
            model_selected = line.rpartition(" ")[-1]
            
# Ensure you are in directory containing garli.conf file.
if os.getcwd() != "/home/lab/Edwin/garli-2.01":
    os.chdir("/home/lab/Edwin/garli-2.01")

# Write to garli.conf file.
ofprefix = raw_input("What would you like ths run to be called? ")
no_bootstrapreps = raw_input("How many bootstrap replications would you like to perform? ")
with open("garli.conf", "r+") as garli_conf:
    configuration = garli_conf.readlines()
    for i,value in enumerate(configuration):
        if value.find("datafname") != -1:
             configuration[i] = "datafname = %s\n" % sequence_file
        if value.find("ofprefix") != -1:
            configuration[i] = "ofprefix = %s\n" % ofprefix
        if value.find("bootstrapreps") != -1:
            configuration[i] = "bootstrapreps = %s\n" % no_bootstrapreps
        if value.find("datatype") != -1:
            configuration("datatype = nucleotide\n")
        if value.find("ratematrix") != -1:
            configuration[i] = "ratematrix = %s\n" % all_possible_models[str(model_selected)][0]
        if value.find("statefrequencies") != -1:
            configuration[i] = "statefrequencies = %s\n" % all_possible_models[str(model_selected)][1]
        if value.find("ratehetmodel") != -1:
            if "+G" in str(model_selected):
                configuration[i] = "ratehetmodel = gamma\n"
            else:
                configuration[i] = "ratehetmodel = none\n"
        if value.find("numratecats") != -1:
            if "+G" in str(model_selected):
                configuration[i] = "numratecats = 4\n"
            else:
                configuration[i] = "numratecats = 1\n"
        if value.find("invariantsites") != -1:
            if "+I" in str(model_selected):
                configuration[i] = "invariantsites = estimate\n"
            else:
                configuration[i] = "invariantsites = none\n"

# Code to run garli here.

# Code to configure and run beast here.