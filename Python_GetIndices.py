input_list = ['datafname', 'ofprefix', 'bootstrapreps', 'datatype',
              'ratematrix', 'statefrequencies', 'ratehetmodel', 'numratecats',
              'invariantsites']

class DefineIndices(object):

    """Compares two user specified lists and returns the indices of matching
       elements as new list."""

    def __init__(self, jMT_file):
        self.jMT_file = jMT_file.readlines()

    def get_indices(self, input_list, input_file):
        indices = []
        for x in input_list:
          indices.extend([num, i] for num, i in enumerate(input_file) if x in i)
        return indices

with open('garli.conf', 'r') as garli_conf:
    JMT = DefineIndices(garli_conf)
    print JMT.get_indices(input_list, JMT.jMT_file)