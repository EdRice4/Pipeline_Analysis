import os
from shutil import copy, move, make_archive
from sys import argv
import subprocess
import linecache
from lxml import etree as ET
from random import randrange
import pyper
from numpy import array, std

script, path_to_sequence = argv

class NexusFile(object):

    """A class in which we will store the name and unique associated with the given
       nexus file."""

    def __init__(self, seq_file):
        self.path = str(seq_file)
        self.sequence_name = seq_file.rpartition("/")[-1]
        self.identifier = str(self.sequence_name) + '_' + str(randrange(0, 999999999))

class GetRange(NexusFile):

    """A class that will return a range of line numbers in a file
       between a user specified start and end sequence"""

    def __init__(self, range_file):
        NexusFile.__init__(self, range_file)

    # Must have empty line at end of sequences to work.
    def get_range(self, start, end):
        with open(self.path, 'r') as range_file:
            range_file = range_file.readlines()
            range_start = 0
            range_end = 0
            for num, line in enumerate(range_file, start=1):
                if start == line.lower():
                    range_start = num
                if end == line.lower():
                    range_end = num
            return range_start, range_end

class Contains(object):

    """Creates list that checks item against iterable and returns matches."""

    def contains(item, iterable):
        matching = []
        if isinstance(item, list) == True:
            for x in item:
                matching.extend(i for i in iterable if x in i)
        else:
            matching.extend(i for i in iterable if item in i)
        return matching

Strumigenys = GetRange(path_to_sequence)

print Strumigenys.path
print Strumigenys.sequence_name
print Strumigenys.identifier
print Strumigenys.get_range('\tmatrix\n', '\n')