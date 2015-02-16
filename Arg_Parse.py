import argparse

arg_parser = argparse.ArgumentParser()
arg_parser.add_argument('-b', '--batch', help=('run script in batch mode'
                       'for multiple nexus files'), action='store_true')
arg_parser.add_argument('-t', '--tolerance', help=('run script in tolerance'
                       'mode for BEAST run'), action='store_true')
arg_parser.add_argument('--tol_value', type=int, help=('value of toelrance '
                        'for BEAST run'))
args = arg_parser.parse_args()

if not args.tol_value:
    args.tol_value = 100

print args.batch, args.tolerance, args.tol_value
