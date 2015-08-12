#!/usr/bin/env python
# -*- coding: utf-8 -*-

# {{{ Header
# Code written by: Edwin Rice
# email: edwinricethe4th@gmail.com
# phone: +1 (513) 426-4187
# github: https://github.com/EdRice4
#
# Initiation date|time: 08/12/2015|11:17:38
# }}}

# {{{ Imports
from time import strftime
from subprocess import Popen, STDOUT, PIPE
from lxml import etree as ET
from random import randrange
from numpy import genfromtxt
from acor import acor
from re import sub
from shutil import move, copy
import argparse
import os
# }}}


# {{{ jModelTest
class jModelTest(object):

    """ {{{ Docstrings

    Run jModelTest and store parameters associated with output.

    }}} """

    # {{{ add_args
    @staticmethod
    def add_args():
        args_jMT = arg_parser.add_argument_group(
                'jMT', 'Arguments for running jModelTest module.'
                )
        args_jMT.add_argument(
                'jMT', type=str, help='Path to jModelTest.jar.'
                )
    # }}}

    # {{{ __init__
    def __init__(self):
        self.jMT_out = 'jModelTest_{0}.out'.format(self._identifier)
        self._jMT_parameters = {}
    # }}}

    # {{{ run_jModeltest
    def run_jModelTest(self):
        jModelTest = (
                'java -jar {0} -d {1} -t fixed '
                '-s 11 -i -g 4 -f -tr 1'
                ).format(args.jMT, self._path)
        jMT_run = Popen(
                jModelTest.split(), stderr=STDOUT, stdout=PIPE,
                universal_newlines=True
                )
        with open(self._JMT_ID, 'w') as output:
            for line in iter(jMT_run.stdout.readline, ''):
                # NOTE: Following if statement only necessary for running in
                # OBCP cluster; can be ommited otherwise.
                if line != 'Cannot perform output.\n':
                    print(line.strip())
                    output.write(str(line))
            jMT_run.stdout.close()
    # }}}

    # {{{ r_jModelTest_output
    def r_jModelTest_output(self, jModelTest_file):
        delimiter = jModelTest_file.index('::Best Models::\n')
        jmtf = jModelTest_file[delimiter + 2:]
        if jmtf[-1].startswith('There'):
            jmtf.pop()
        names = jmtf[0]
        model = jmtf[2]
        return names, model
    # }}}

    # {{{ r_jModelTest_names
    def r_jModelTest_names(self, names):
        names = names.split('\t')
        names = filter(None, names)
        names = map(lambda x: x.strip(), names)
        return names
    # }}}

    # {{{ r_jModelTest_model
    def r_jModelTest_model(self, model):
        model = model.replace('\t', ' ')
        model = model.split(' ')
        model = filter(None, model)
        model = model[1:]
        model = map(lambda x: x.strip(), model)
        return model
    # }}}

    # {{{ r_jModelTest_parameters
    def r_jModelTest_parameters(self, jModelTest_file):
        names, model = self._r_jModelTest_output(jModelTest_file)
        names = self._r_jModelTest_names(names)
        model = self._r_jModelTest_model(model)
        self._jMT_parameters = dict((i, j) for i, j in zip(names, model))
    # }}}
# }}}


# {{{ Garli
class Garli(jModelTest):

    """ {{{ Docstrings

    Run garli and store parameters associated with output.

    }}} """

    # {{{ models
    models = {
            'JC': ['1rate', 'equal'],
            'F81': ['1rate', 'estimate'],
            'K80': ['2rate', 'equal'],
            'HKY': ['2rate', 'estimate'],
            'TrNef': ['(0 1 0 0 2 0)', 'equal'],
            'TrN': ['(0 1 0 0 2 0)', 'estimate'],
            'TPM1': ['(0 1 2 2 1 0)', 'equal'],
            'TPM1uf': ['(0 1 2 2 1 0)', 'estimate'],
            'TPM2': ['(0 1 0 2 1 2)', 'equal'],
            'TPM2uf': ['(0 1 0 2 1 2)', 'estimate'],
            'TPM3': ['(0 1 2 0 1 2)', 'equal'],
            'TPM3uf': ['(0 1 2 0 1 2)', 'estimate'],
            'K3P': ['(0 1 2 2 1 0)', 'equal'],
            'K3Puf': ['(0 1 2 2 1 0)', 'estimate'],
            'TM1ef': ['(0 1 2 2 3 0)', 'equal'],  # Remove 'I' for translate.
            'TM1': ['(0 1 2 2 3 0)', 'estimate'],  # Remove 'I' for translate.
            'TM2ef': ['(0 1 0 2 3 2)', 'equal'],
            'TM2': ['((0 1 0 2 3 2))', 'estimate'],
            'TM3ef': ['(0 1 2 0 3 2)', 'equal'],
            'TM3': ['(0 1 2 0 3 2)', 'estimate'],
            'TVMef': ['(0 1 2 3 1 4)', 'equal'],
            'TVM': ['(0 1 2 3 1 4)', 'estimate'],
            'SYM': ['6rate', 'equal'],
            'GTR': ['6rate', 'estimate']
            }
    # }}}

    # {{{ add_args
    @staticmethod
    def add_args():
        args_garli = arg_parser.add_argument_group(
                'garli', 'Arguments for running garli module.'
                )
        args_garli.add_argument(
                '-g', '--garli', help='Run garli analysis.',
                action='store_true')
        args_garli.add_argument(
                '--bstr', type=int, help=(
                        '# of bootstrap replications for garli analysis, if '
                        'applicable.'
                        ),
                default=0
                )
    # }}}

    # {{{ file_edit
    def edit_garli_conf(self, garli_conf, lines_to_edit, values_to_insert):

        """ {{{ Docstrings

        Returns a modified garli configuration file, given the original
        file, a list corresponding to the string values of the lines to be
        edited, and the values which are to be inserted.

        The values of 'lines_to_edit' and 'values_to_insert' arguments should
        be in corresponding order so that the first value of the former
        corresponds the the value you wish that parameter to have in the later.

        }}} """

        for i, j in zip(lines_to_edit, values_to_insert):
            garli_conf[garli_conf.index(i)] = '{0}'.format(
                    garli_conf[garli_conf.index(i)].strip() + j + '\n'
                    )
        return garli_conf
    # }}}

    # {{{ w_garli_conf
    def w_garli_conf(self, garli_file):
        model_selected = self._jMT_parameters['Model']
        het = '+G' in model_selected
        inv = '+I' in model_selected
        model_selected = model_selected.translate(None, '+IG')
        garli_params = [
                'datafname =\n', 'ofprefix =\n',
                'bootstrapreps =\n', 'ratematrix =\n',
                'statefrequencies =\n', 'ratehetmodel =\n',
                'numratecats =\n', 'invariantsites =\n'
                ]
        garli_values = [
                self._path, self._identifier, str(args.bstr),
                Garli.models[str(model_selected)][0],
                Garli.models[str(model_selected)][1]
                ]
        if het:
            garli_values.extend(['gamma', '4'])
        else:
            garli_values.extend(['none', '1'])
        if inv:
            garli_values.append('estimate')
        else:
            garli_values.append('none')
        garli_file = self._file_edit(garli_file, garli_params, garli_values)
        with open('garli_%s.conf' % self._identifier, 'w+') as garli_output:
            for i in garli_file:
                garli_output.write(i)
    # }}}

    # {{{ run_garli
    def run_garli(self):
        garli = './Garli -b garli_%s.conf' % self._identifier
        garli_run = Popen(
                garli.split(), stderr=STDOUT, stdout=PIPE, stdin=PIPE
                )
        for line in iter(garli_run.stdout.readline, ''):
            print(line.strip())
        garli_run.stdout.close()
    # }}}
# }}}


# {{{ BEAST
class BEAST(Garli):

    """ {{{ Docstrings
    Run BEAST and store parameters associated with output.
    }}} """

    # {{{ add_args
    @staticmethod
    def add_args():
        args_BEAST = arg_parser.add_argument_group(
                'BEAST', 'Arguments for running BEAST module.'
                )
        args_BEAST.add_argument(
                  'BEAST', type=str, help='Path to beast.jar.'
                  )
        args_BEAST.add_argument(
                '--MCMC_BEAST', type=int, help=(
                        'Length of MCMC chain for BEAST '
                        'analysis.'),
                default=50000000)
        args_BEAST.add_argument(
                '--burnin_BEAST', type=float, help=(
                        'Burnin (%%) for BEAST analysis.'
                        ),
                default=0.25)
        args_BEAST.add_argument(
                '--store_every', type=int, help=(
                            'Sample interval for BEAST analysis.'
                            ),
                default=1000)
        args_BEAST.add_argument(
                '-t', '--tolerance', type=int, help=(
                        'Run script in tolerance mode '
                        'for BEAST analysis.'),
                default=0)
        args_BEAST.add_argument(
                '--lcom', type=str, help=(
                        'Path to logcombiner. Only necessary if '
                        'running in tolerance mode.')
                )
    # }}}

    # {{{ __init__
    def __init__(self):
        self._BEAST_XML = 'BEAST_{0}.xml'.format(
                self._identifier
                )
        self._BEAST_ID = 'BEAST_{0}.out'.format(
                self._identifier
                )
    # }}}

    # {{{ JC_F81
    def JC_F81(self, xml_nodes):
        for i in xml_nodes:
            i.text = '1.0'
    # }}}

    # {{{ K80_HKY
    def K80_HKY(self, xml_nodes):
        for i in xml_nodes:
            if 'rateAG.s:' in i.get('id') or 'rateCT.s:' in i.get('id'):
                i.text = self._jMT_parameters['titv']
            else:
                i.text = '1.0'

    sub_models = {'JC': JC_F81, 'F81': JC_F81,
                  'K80': K80_HKY, 'HKY': K80_HKY}
    # }}}

    # {{{ calculate_statistics
    def calculate_statistics(self, data_file):
        data = genfromtxt(data_file, comments='#', usecols=range(1, 17))[1:]
        data = zip(*data)[1:]
        stats = map(lambda x: acor(x), data)
        auto_cor_times = zip(*stats)[0]
        chain_length = int(args.MCMC_BEAST * (1 - args.burnin_BEAST))
        eff_sample_size = map(lambda x: chain_length / x, auto_cor_times)
        return eff_sample_size
    # }}}

    # {{{ w_beast_submodel
    def w_beast_submodel(self):
        model_selected = self._jMT_parameters['Model']
        het = '+G' in model_selected
        inv = '+I' in model_selected
        model_selected = model_selected.translate(None, '+IG')
        run.set('chainLength', '%s' % args.MCMC_BEAST)
        run.set('preBurnin', '0')
        log.set('logEvery', '%s' % args.store_every)
        screen_log.set('logEvery', '%s' % args.store_every)
        tree_log.set('logEvery', '%s' % args.store_every)
        if Garli.models[str(model_selected)][1] == 'estimate':
            freq = ET.SubElement(
                    state, 'parameter',
                    attrib={
                            'dimension': '4',
                            'id': 'freqParameter.s:%s' % self._sequence_name,
                            'lower': '0.0', 'name': 'stateNode',
                            'upper': '1.0'
                            }
                    )
            freq.text = '0.25'
            freq_log = ET.SubElement(
                    log, 'parameter',
                    attrib={
                            'idref': 'freqParameter.s:%s' % self._sequence_name,
                            'name': 'log'
                            }
                    )
        if Garli.models[str(model_selected)][1] == 'equal':
            freq = ET.SubElement(
                    substmodel, 'frequencies',
                    attrib={
                            'data': '@%s' % self._sequence_name,
                            'estimate': 'false',
                            'id': 'equalFreqs.s:%s' % self._sequence_name,
                            'spec': 'Frequencies'
                            }
                    )
        if het:
            sitemodel.set('gammaCategoryCount', '4')
            gamma_shape = ET.SubElement(
                    sitemodel, 'parameter',
                    attrib={
                            'estimate': 'false',
                            'id': 'gammaShape.s:%s' % self._sequence_name,
                            'name': 'shape'
                            }
                    )
            gamma_shape.text = self._jMT_parameters['gamma']
        else:
            gamma_shape = ET.SubElement(
                    sitemodel, 'parameter',
                    attrib={
                            'estimate': 'false',
                            'id': 'gammaShape.s:%s' % self._sequence_name,
                            'name': 'shape'
                            }
                    )
            gamma_shape.text = '0.0'
        if inv:
            p_inv = ET.SubElement(
                    sitemodel, 'parameter',
                    attrib={
                            'estimate': 'false',
                            'id': 'proportionInvariant.s:%s' % self._sequence_name,
                            'lower': '0.0', 'name': 'proportionInvariant',
                            'upper': '1.0'
                            }
                    )
            p_inv.text = self._jMT_parameters['pInv']
        else:
            p_inv = ET.SubElement(
                    sitemodel, 'parameter',
                    attrib={
                            'estimate': 'false',
                            'id': 'proportionInvariant.s:%s' % self._sequence_name,
                            'lower': '0.0', 'name': 'proportionInvariant',
                            'upper': '1.0'
                            }
                    )
            p_inv.text = '0.0'
    # }}}

    # {{{ w_beast_rates
    def w_beast_rates(self):
        xml_nodes = []
        model_selected = self._jMT_parameters['Model'].translate(None, '+IG')
        for element in substmodel.iter():
            if 'rateAC.s:' in element.get('id'):
                rateAC = element
                xml_nodes.append(element)
            if 'rateAG.s:' in element.get('id'):
                rateAG = element
                xml_nodes.append(element)
            if 'rateAT.s:' in element.get('id'):
                rateAT = element
                xml_nodes.append(element)
            if 'rateCG.s:' in element.get('id'):
                rateCG = element
                xml_nodes.append(element)
            if 'rateCT.s:' in element.get('id'):
                rateCT = element
                xml_nodes.append(element)
            if 'rateGT.s:' in element.get('id'):
                rateGT = element
                xml_nodes.append(element)
        if BEAST.sub_models.get(model_selected):
            BEAST.sub_models[model_selected](self, xml_nodes)
        else:
            rateAC.text = '%s' % self._jMT_parameters['Ra']
            rateAG.text = '%s' % self._jMT_parameters['Rb']
            rateAT.text = '%s' % self._jMT_parameters['Rc']
            rateCG.text = '%s' % self._jMT_parameters['Rd']
            rateCT.text = '%s' % self._jMT_parameters['Re']
            rateGT.text = '%s' % self._jMT_parameters['Rf']
    # }}}

    # {{{ get_range
    def get_range(self, nexus_file, start, end):

        """ {{{ Docstrings

        Returns the index of a user-specified start and end sequence,
        given these and a list (for instance, a file read in with the
        "readlines()" function.

        The "start" and "end" arguments must match corresponding lines in
        range_file exactly, including any whitespace characters.

        For instance, in parsing the nexus file, the line immediately before
        the data block (the section containing the sequences and their
        respective IDs) should be "matrix\n" and the line immediately below
        should be ";\n" to ensure that every sequence is parsed, nothing more,
        nothing less.

        }}} """

        range_start = nexus_file.index(start)
        range_end = nexus_file.index(end)
        return range_start, range_end
    # }}}

    # {{{ w_beast_taxon
    def w_beast_taxon(self, nexus_file):
        sequence_start, sequence_end = self._get_range(
                nexus_file, 'matrix\n', ';\n'
                )
        sequence_start += 1
        sequence_end -= 1
        for line in nexus_file:
            while sequence_start <= sequence_end:
                species_id = (nexus_file[int(sequence_start)].rpartition(
                              "\t")[0]).strip()
                species_sequence = (
                        nexus_file[int(sequence_start)].rpartition("\t")[-1]
                        ).strip()
                sequence = ET.SubElement(data, 'sequence', attrib={
                                         'id': 'seq_%s' % species_id,
                                         'taxon': '%s' % species_id,
                                         'totalcount': '4',
                                         'value': '%s' % species_sequence})
                sequence_start += 1
    # }}}

    # {{{ beast_finalize
    def beast_finalize(self):
        log.set('fileName', self._BEAST_ID)
        beast.write(self._BEAST_XML, pretty_print=True, xml_declaration=True,
                    encoding='UTF-8', standalone=False)
        with open(self._BEAST_XML, 'r+') as beast_xml_file:
            beast_xml = beast_xml_file.read()
        beast_xml = sub('replace_taxon', self._sequence_name, beast_xml)
        with open(self._BEAST_XML, 'w') as beast_xml_file:
            beast_xml_file.write(beast_xml)
    # }}}

    # {{{ run_beast
    def run_beast(self):
        run = self._identifier + '_RUN_1'
        os.mkdir(run)
        BEAST = '%s -prefix %s -seed %s %s' % (args.BEAST, run,
                                               str(randrange(0, 999999)),
                                               self._BEAST_XML)
        beast_run = Popen(BEAST.split(), stderr=STDOUT, stdout=PIPE,
                          stdin=PIPE)
        for line in iter(beast_run.stdout.readline, ''):
            print(line.strip())
        beast_run.stdout.close()
    # }}}

    # {{{ resume_beast
    def resume_beast(self):
        ess = 1
        run_count = 1
        while ess:
            run = self._identifier + '_RUN_' + str(run_count)
            os.mkdir(run)
            BEAST = '%s -prefix %s -seed %s %s' % (args.BEAST, run,
                                                   randrange(0, 999999999),
                                                   self._BEAST_XML)
            beast_run = Popen(BEAST.split(), stderr=STDOUT, stdout=PIPE,
                              stdin=PIPE)
            for line in iter(beast_run.stdout.readline, ''):
                print(line.strip())
            beast_run.stdout.close()
            run_count += 1
            ess = self._calculate_statistics(run + '/' + self._BEAST_ID)
            ess = filter(lambda x: x < args.tolerance, ess)
    # }}}

    # {{{ log_combine
    def log_combine(self):
        cwd = os.getcwd()
        fid = os.listdir(cwd)
        bdirs = filter(lambda x: '_RUN_' in x, fid)
        if len(bdirs) > 1:
            bdirs = map(lambda x: '-log ' + x + '/' + self._BEAST_ID, bdirs)
            com = './%s %s -b %s -o MASTER_%s' % (args.lcom,
                                                  ' '.join(bdirs),
                                                  args.burnin_BEAST,
                                                  self._BEAST_ID)
            lcom = Popen(com.split(), stderr=STDOUT, stdout=PIPE, stdin=PIPE)
            for line in iter(lcom.stdout.readline, ''):
                print(line.strip())
            lcom.stdout.close()
    # }}}
# }}}


# {{{ bGMYC
class bGMYC(BEAST):

    """ {{{ Docstrings
    Run bGMYC with Rscript and store output.
    }}} """

    # {{{ add_args
    @staticmethod
    def add_args():
        args_bGMYC = arg_parser.add_argument_group(
                'bGMYC', 'Arguments for running bGMYC module.'
                )
        args_bGMYC.add_argument(
                '--MCMC_bGMYC', type=int, help=(
                        'Length of MCMC chain for bGMYC '
                        'analysis.'
                        ),
                default=50000000)
        args_bGMYC.add_argument(
                '--burnin_bGMYC', type=float, help=(
                        'Burnin (%%) for bGMYC analysis.'
                        ),
                default=0.25)
        args_bGMYC.add_argument(
                '--thinning', type=int, help=(
                        'Sample interval for bGMYC analysis.'
                        ),
                default=10000)
        args_bGMYC.add_argument(
                '--bGMYC_params', type=str, help=(
                        'Name of the file containing additional arguments for '
                        'the bGMYC, if applicable. These parameters should be '
                        'specified in a tab delimited format along with the '
                        'taxon name, where the taxon name corresponds to the '
                        'respecitve nexus file sans the \'.nex\' extension. '
                        'For instance, if I wanted to run a bGMYC analysis on '
                        'Periplaneta americana, the American cockroach, and '
                        'wanted to modify the \'t1\' and \'start\' variables '
                        '(see documentation provided by Noah for explanation '
                        'of parameters), then my files would perhaps look '
                        'like: P_americana.nex, P_americana.txt and the .txt '
                        'file would contain: P_americana\\t-t1=32\\tstart1=0'
                        '\\tstart2=0\\tstart3=0.5. Notice how each value of '
                        'start vector must be specified seperately.'
                        ),
                )
    # }}}

    # {{{ build_dict_bGMYC_params
    # Only run once.
    @staticmethod
    def build_dict_bGMYC_params(dict_file):
        dictionary = {}
        with open(dict_file, 'r') as d:
            d = d.readlines()
        d = map(lambda x: x.strip(), d)
        d = map(lambda x: x.split('\t'), d)
        for i in d:
            dictionary[i[0]] = i[1:]
        return dictionary
    # }}}

    # {{{ bGMYC
    def bGMYC(self, parameter_dict):
        burnin_bGMYC = round(args.MCMC_bGMYC * args.burnin_bGMYC)
        if parameter_dict.get(self._sequence_name):
            parameters = parameter_dict[self._sequence_name]
        else:
            parameters = []
        os.chdir(self._master_dir)
        cwd = os.getcwd()
        fid = os.listdir(cwd)
        bdirs = filter(lambda x: '_RUN_' in x, fid)
        for i in bdirs:
            os.chdir(i)
            cwd = os.getcwd()
            fid = os.listdir(cwd)
            Rscript = (
                    'Rscript --save ../../bGMYC.R --args -taxon={0} -id={1} '
                    '-mcmc={2} -burnin={3} -thinning={4} {5}'
                    ).format(
                            self._sequence_name, self._identifier,
                            args.MCMC_bGMYC, burnin_bGMYC, args.thinning,
                            ' '.join(parameters)
                            )
            bGMYC_run = Popen(Rscript.split(), stderr=STDOUT, stdout=PIPE,
                              stdin=PIPE)
            for line in iter(bGMYC_run.stdout.readline, ''):
                print(line.strip())
            bGMYC_run.stdout.close()
            os.chdir('../')
    # }}}
# }}}


# {{{ CleanUp
class CleanUp(bGMYC):

    """ {{{ Docstrings
    A class used to consolidate all output.
    }}} """

    # {{{ __init__
    def __init__(self):
        self._master_dir = self._identifier + '_MASTER'
    # }}}

    # {{{ clean_up
    def clean_up(self):
        cwd = os.getcwd()
        files_in_dir = os.listdir(cwd)
        output_files = filter(lambda x: self._identifier in x, files_in_dir)
        os.mkdir(self._master_dir)
        for i in output_files:
            move(i, self._master_dir)
        copy(self._path, self._master_dir)
    # }}}
# }}}


# {{{ IterRegistry
class IterRegistry(type):

    """ {{{ Docstrings
    A metaclass to allow for iteration over instances of NexusFile class.
    }}} """

    # {{{ __iter__
    def __iter__(cls):
        return iter(cls.registry)
    # }}}
# }}}


# {{{ NexusFile
class NexusFile(CleanUp):

    """ {{{ Docstrings
    A class in which we will store the parameters associated with the
    given nexus file.
    }}} """

    # {{{ __metaclass__
    __metaclass__ = IterRegistry
    registry = []
    # }}}

    # {{{ add_args
    @staticmethod
    def add_args():
        args_nex = arg_parser.add_argument_group(
                'Nexus', 'Arguments for parsing nexus files.'
                )
        args_nex.add_argument(
                '-b', '--batch', help=(
                        'Run script in batch mode for multiple nexus files. '
                        'Note: All nexus files should have the extension '
                        '\'.nex\', NOT \'.nexus\' and the line immediately '
                        'above the data block (section containing the '
                        'sequences and their respective IDs) should read '
                        '\'matrix\\n\' while the line immediately below '
                        'should read \';\\n\'. Furthermore, if running in '
                        'batch mode, ensure that the nexus files are the only '
                        'files present in the directory containing the string '
                        '\'nex\' in their name, including the extension.'
                        ),
                action='store_true')
    # }}}

    # {{{ __init__
    def __init__(self, path):
        self._path = str(path)
        self._sequence_name = self._path.replace('.nex', '')
        self._identifier = '{0}_{1}'.format(
                self._sequence_name, randrange(0, 999999999)
                )
        jModelTest.__init__(self)
        BEAST.__init__(self)
        CleanUp.__init__(self)
        self._registry.append(self)
    # }}}

    # {{{ write_call_file
    def write_call_file(self, bGMYC_parameters):

        """ {{{ Docstrings
        For each instance of NexusFile class, writes a name file, corresponding
        to the unique identifier, that contains: The run initiation date/time,
        the sequence path, the sequence identifier, and how the script was
        called (the Namespace [arguments given to script]).
        }}} """

        call_file = 'call_{0}.txt'.format(
                self._identifier
                )
        # Local date (MM/DD/YY) and local time (HH:MM:SS [24 fmt])
        call_time = 'Initiation date|time: {0}\n'.format(
                strftime('%x|%X')
                )
        call_id = 'Sequence file: {0}\n'.format(
                self._identifier
                )
        # Convert args to dictionary
        opts = vars(args)
        with open(call_file, 'w') as call:
            call.write(call_time)
            call.write(call_id)
            for i in opts:
                # bGMYC parameters handled by subsequent if statment
                if i != 'bGMYC_params':
                    f = '{0}={1}\n'.format(
                            i, opts[i]
                            )
                    call.write(f)
            if bGMYC_parameters.get(self._sequence_name):
                call.write('bGMYC parameters: ')
                call.write(str(bGMYC_parameters[self._sequence_name]))
            else:
                call.write('bGMYC parameters: Defaults')
    # }}}
# }}}


# {{{ ArgParser
arg_parser = argparse.ArgumentParser(
        prog='Pipeline',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description=(
                'A modular python script providing the backbone for '
                'customizable, ad hoc pipeline analyses. For instance, '
                'originally developed to function between jModelTest, Garli, '
                'BEAST and bGMYC. Also provides batch functionality for '
                'relatively large datasets and supports HPC environments.'
                )
        )

# Run add_args for each class when passing '-h' flag and prior to instantiating
# instances of any class.
if __name__ == '__main__':
    jModelTest.add_args()
    Garli.add_args()
    BEAST.add_args()
    bGMYC.add_args()
    NexusFile.add_args()
args = arg_parser.parse_args()
# }}}


# {{{ XML Parser
XML_parser = ET.XMLParser(remove_blank_text=True)
beast = ET.parse('Standard.xml', XML_parser)
data = beast.find('data')
run = beast.find('run')
for element in run.iter():
    if element.tag == 'state':
        state = element
    if element.tag == 'substModel':
        substmodel = element
    if element.tag == 'siteModel':
        sitemodel = element
for element in run.iterfind('logger'):
    if element.get('id') == 'tracelog':
        log = element
    if element.get('id') == 'screenlog':
        screen_log = element
    if 'treelog.t:' in element.get('id'):
        tree_log = element
# }}}


# {{{ Define nexus files; batch
if args.batch:
    cwd = os.getcwd()
    files_in_dir = os.listdir(cwd)
    nexus_files = filter(lambda x: '.nex' in x, files_in_dir)
else:
    nexus_files = []
    print('The program will prompt you for the path to each sequence file.')
    no_runs = raw_input('How many runs would you like to perform? ')
    for i in range(int(no_runs)):
        nexus_files.append(raw_input('Path to sequence file: '))
# }}}


# {{{ Instantiate instances of NexusFile class
for i in nexus_files:
    NexusFile(i)
# }}}


# {{{ Read bGMYC dictionary file
if args.bGMYC_params:
    bGMYC_parameters = NexusFile.build_dict_bGMYC_params(args.bGMYC_params)
else:
    bGMYC_parameters = {}
# }}}


# {{{ Run
for sequence in NexusFile:
    print('-----------------------------------------------------------------')
    print('Sequence file: %s' % sequence.path)
    print('Run identifier: %s' % sequence.identifier)
    print('Garli bootstrap replications: %s' % args.bstr)
    print('MCMC BEAST: %s' % args.MCMC_BEAST)
    print('Burnin BEAST: %s' % args.burnin_BEAST)
    if args.tolerance:
        print('Tolerance: %s' % args.tolerance)
    print('Sample frequency BEAST: %s' % args.store_every)
    print('MCMC bGMYC: %s' % args.MCMC_bGMYC)
    print('Burnin bGMYC: %s' % args.burnin_bGMYC)
    print('Sample frequency bGMYC: %s' % args.thinning)
    print('-----------------------------------------------------------------')
    sequence.write_call_file(bGMYC_parameters)
    with open(sequence.path, 'r') as nex:
        nexus_file = nex.readlines()
    sequence.run_jModelTest()
    with open(str(sequence.JMT_ID), 'r') as JMT_output:
        JMT_output = JMT_output.readlines()
    sequence.r_jModelTest_parameters(JMT_output)
    if args.garli:
        with open('garli.conf', 'r') as garli_conf:
            garli_conf = garli_conf.readlines()
        sequence.w_garli_conf(garli_conf)
        sequence.run_garli()
    sequence.w_beast_submodel()
    sequence.w_beast_rates()
    sequence.w_beast_taxon()
    sequence.beast_finalize()
    if args.tolerance:
        sequence.resume_beast()
        sequence.log_combine()
    else:
        sequence.run_beast()
    sequence.clean_up()
    sequence.bGMYC(bGMYC_parameters)
# }}}
