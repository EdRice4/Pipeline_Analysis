from random import randrange
from sys import argv

script, path_to_sequence, path_to_jModelTest = argv

class NexusFile(object):

    """A class in which we will store the parameters associated with the given nexus file."""

    def __init__(self, path_to_sequence):
        self.sequence_name = path_to_sequence.rpartition("/")[-1]
        self.identifier = str(self.sequence_name) + '_' + str(randrange(0, 999999999))

    def run_jModelTest():
        jModelTest = 'java -jar %s -d %s -t fixed -o jModelTest_%s_.out -s 11 -i -g 4 -f -tr 1' % (path_to_jModelTest, path_to_sequence, identifier)
        subprocess.call(jModelTest.split())

Nexus_File = NexusFile(path_to_sequence)

print Nexus_File.sequence_name
print Nexus_File.identifier

# def r_jModelTest_model(jModelTest_file):
#     for line in jModelTest_file:
#         if 'Model = ' in line:
#             model_selected = line.rpartition(' ')[-1]
#     self.model = model_selected.replace('\n', '') # return

# def r_jModelTest_parameters(jModelTest_file):
#     for line in jModelTest_file:
#         if 'freqA' in line:
#             freqA = line.rpartition(' ')[-1]
#         if 'freqC' in line:
#             freqC = line.rpartition(' ')[-1]
#         if 'freqG' in line:
#             freqG = line.rpartition(' ')[-1]
#         if 'freqT' in line:
#             freqT = line.rpartition(' ')[-1]
#         if 'R(a) [AC]' in line:
#             Ra = line.rpartition(' ')[-1]
#         if 'R(b)' in line:
#             Rb = line.rpartition(' ')[-1]
#         if 'R(c)' in line:
#             Rc = line.rpartition(' ')[-1]
#         if 'R(d)' in line:
#             Rd = line.rpartition(' ')[-1]
#         if 'R(e)' in line:
#             Re = line.rpartition(' ')[-1]
#         if 'R(f)' in line:
#             Rf = line.rpartition(' ')[-1]
#         if "p-inv" in line:
#             p_inv = line.rpartition(' ')[-1]
#         if 'gamma shape' in line:
#             gamma_shape = line.rpartition(' ')[-1]
#     parameters.append(freqA)
#     parameters.append(freqC)
#     parameters.append(freqG)
#     parameters.append(freqT)
#     parameters.append(Ra)
#     parameters.append(Rb)
#     parameters.append(Rc)
#     parameters.append(Rd)
#     parameters.append(Re)
#     parameters.append(Rf)
#     parameters.append(p_inv)
#     parameters.append(gamma_shape)
#     for num,item in enumerate(parameters):
#         item = item.replace('\n', '')
#         parameters[num] = item
#     return parameters