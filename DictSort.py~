import argparse
import numpy as np
from StringIO import StringIO


def GetLines(nexus, header, footer):

    """Get line numbers to use in subsequent sorting."""

    with open(nexus, 'r') as nex:
        nex = nex.readlines()
    head = nex.index(header) + 1
    foot = len(nex) - nex.index(footer)
    return head, foot


def SortDictionary(nexus, header, footer, delimiter):

    """Takes nexus file and sorts into dictionary, organized by taxon."""

    boundaries = GetLines(nexus, header, footer)
    with open(nexus, 'r') as nex:
        nex = nex.read()
    data = np.genfromtxt(StringIO(nex), dtype=str, skip_header=boundaries[0],
                         skip_footer=boundaries[1])
    taxons = map(lambda x: (x.split(delimiter))[-1], data.T[0])
    taxons = list(set([x for x in taxons if x != 'withdrawn' and x != 'CASENT']))
    for i in taxons:
        individuals = filter(lambda x: i in x[0], data)
        nex_file_header = [
            '#NEXUS\n', 'begin data;',
            '\tdimensions ntax=%s nchar=%s;' % (len(individuals),
                                                len(individuals[0][1])),
            '\tformat datatype=dna missing=? gap=-;', 'matrix'
            ]
        nex_file_footer = ['end;', ';']
        np.savetxt(i, individuals, fmt='%s', delimiter='\t', newline='\n',
                   header='\n'.join(nex_file_header),
                   footer='\n'.join(nex_file_footer),
                   comments='')

arg_parser = argparse.ArgumentParser()
arg_parser.add_argument('nex_file', type=str, help='Nexus file to be sorted')
arg_parser.add_argument('-head', '--header', type=str, help=('Rows in upper '
                        'boundary to be excluded'))
arg_parser.add_argument('-foot', '--footer', type=str, help=('Rows in lower '
                        'boundary to be excluded'))
arg_parser.add_argument('-d', '--delimiter', type=str, help=('Delimiter '
                        'separating components of identifier'))
args = arg_parser.parse_args()

if not args.header:
    args.header = 'matrix\n'
if not args.footer:
    args.footer = ';\n'
if not args.delimiter:
    args.delimiter = '|'

SortDictionary(args.nex_file, args.header, args.footer, args.delimiter)
