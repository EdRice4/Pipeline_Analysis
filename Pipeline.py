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
from StringIO import StringIO
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

        """ {{{ Docstrings

        Add argument group "jMT" to namespace and subsequent pertinent
        arguments to aforementioned group.

        }}} """

        args_jMT = arg_parser.add_argument_group(
                'jMT', 'Arguments for running jModelTest module.'
                )
        args_jMT.add_argument(
                'jMT', type=str, help='Path to jModelTest.jar.'
                )
    # }}}

    # {{{ __init__
    def __init__(self):

        """ {{{ Docstrings

        Upon instantiating instance of class, run functions and store
        parameters.

        }}} """

        self._jMT_out = 'jModelTest_{0}.out'.format(self._identifier)
        self.run_jModelTest()
        self._jMT_parameters = self.r_jModelTest_parameters(self._jMT_out)
    # }}}

    # {{{ run_jModeltest
    def run_jModelTest(self):

        """ {{{ Docstrings

        Run jModelTest by spawning child process, utilizing "Popen" function
        provided by "subprocess" python module. The output/errors of this
        process are then subsequently printed, to stdout and written to a file,
        in real-time.

        }}} """

        # Specify child process, including any pertinent arguments; see
        # jModelTest documentation for explanantion of arguments
        # ::MODIFIABLE::
        # NOTE: If you would like to modify arguments passed to jModelTest,
        # simply format the following string in a matter of your choosing.
        # You may also have to change the manner in which jModelTest is
        # called, depending on your system.
        jModelTest = (
                'java -jar {0} -d {1} -t fixed -s 11 -i -g 4 -f -v -a -BIC '
                '-AIC -AICc -DT'
                ).format(args.jMT, self._path)
        # Spawn child process and run
        jMT_run = Popen(
                jModelTest.split(), stderr=STDOUT, stdout=PIPE,
                universal_newlines=True
                )
        # Open stdout of child process and print/write in real-time
        with open(self._JMT_ID, 'w') as output:
            for line in iter(jMT_run.stdout.readline, ''):
                print(line.strip())
                output.write(str(line))
            # Close stdout
            jMT_run.stdout.close()
    # }}}

    # {{{ r_jModelTest_output
    def r_jModelTest_output(self, jModelTest_file):

        """ {{{ Docstrings

        Given the name of the jModelTest output file (as a string), opens the
        file in read mode and reads it into a list which is then parsed
        (here and in subsequent functions; see below) for the pertinent
        selected model paramters at the end of the file.

        NOTE: This function does not support comparison of selected models
        between different selection criterion; to do so would require
        human interference which does not coincide with the purpose of this
        script. Rather, it simply selects the model output "first."

        }}} """

        # Open jModelTest output in read model
        with open(jModelTest_file, 'r') as jmt_out:
            # Read into list
            jmt_out = jmt_out.readlines()
        # Get beginning psoition of selected model block
        delimiter = jmt_out.index('::Best Models::\n')
        # Truncate the output
        jmt_out = jmt_out[delimiter + 2:]
        # Get the names of the variables
        variables = jmt_out[0]
        # Get the values of the variables
        values = jmt_out[2]
        return variables, values
    # }}}

    # {{{ r_jModelTest_variables
    def r_jModelTest_variables(self, variables):

        """ {{{ Docstrings

        Given a string of variable names (as parsed by r_jModelTest_output),
        further parses them into a list, stripping the values, and formatting
        them, in order to generate a "pretty" dictionary.

        }}} """

        # Split string by occurences of tab "\t" character
        variables = variables.split('\t')
        # Filter out empty values
        variables = filter(None, variables)
        # Strip values of leading and trailing whitespace characters
        variables = map(lambda x: x.strip(), variables)
        return variables
    # }}}

    # {{{ r_jModelTest_values
    def r_jModelTest_values(self, values):

        """ {{{ Docstrings

        Given a string of variable values (as parsed by r_jModelTest_output),
        further parses them into a list, stripping the values, and formatting
        them, in order to generate a "pretty" dictionary.

        }}} """

        # Replace tab "\t" character with blank space; not every tab character
        # in values line corresponds to a tab character in variables line, so
        # in order for len(values) == len(variables), must split by another
        # method
        values = values.replace('\t', ' ')
        # Split string by occurrences of space
        values = values.split(' ')
        # Filter out empty values
        values = filter(None, values)
        # Do not want selection criteria as value
        values = values[1:]
        # Strip values of leading and trailing whitespace characters
        values = map(lambda x: x.strip(), values)
        return values
    # }}}

    # {{{ r_jModelTest_parameters
    def r_jModelTest_parameters(self, jModelTest_file):

        """ {{{ Docstrings

        Concatenates r_jModelTest* functionality; performing all necessary
        steps to generate "pretty" dictionary in format of:

                dictionary = {
                        'variable' : 'value'
                        'variable' : 'value'
                        }

        }}} """

        # Get variables and corresponding values as strings
        variables, values = self.r_jModelTest_output(jModelTest_file)
        # Parse variables into list
        variables = self.r_jModelTest_variables(variables)
        # Parse values into list
        values = self.r_jModelTest_values(values)
        # Generate dictionary
        jMT_parameters = dict((i, j) for i, j in zip(variables, values))
        return jMT_parameters
    # }}}
# }}}


# {{{ Garli
class Garli(jModelTest):

    """ {{{ Docstrings

    Run garli and store parameters associated with output.

    }}} """

    # {{{ add_args
    @staticmethod
    def add_args():

        """ {{{ Docstrings

        Add argument group "garli" to namespace and subsequent pertinent
        arguments to aforementioned group.

        }}} """

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

    # {{{ r_garli_conf
    @staticmethod
    def r_garli_conf():

        """ {{{ Docstrings

        Reads in garli.conf template file as a list. Method is static because
        only necessary to run once; do not need to run upon every
        instantiation of Garli class.

        }}} """

        # Open in read mode
        with open('garli.conf', 'r') as garli_conf:
            # Read in as list
            garli_conf = garli_conf.readlines()
        # Strip leading and trailing white characters on every line
        garli_conf = map(lambda x: x.strip(), garli_conf)
        return garli_conf
    # }}}

    # {{{ models
    # Dictionary utilized to store and reference pertienent parameters
    # (ratematrix and statefrequenceis) for each respective substitution model
    # NOTE: TM1ef and TM1 are missing 'I' string because all occurences of
    # 'I' and 'G' are later removed from selected model to make number of
    # models more tractable, otherwise would have had to sepcify 4 distinct
    # models, one without invarant and gamma, one with just invariant, etc.
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
            'TM1ef': ['(0 1 2 2 3 0)', 'equal'],  # Remove 'I' for translate
            'TM1': ['(0 1 2 2 3 0)', 'estimate'],  # Remove 'I' for translate
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

    # {{{ __init__
    def __init__(self):

        """ {{{ Docstrings

        Upon instantiating instance of class, run functions and store
        parameters.

        }}} """

        self.w_garli_conf(garli_conf)
        self.run_garli()
    # }}}

    # {{{ edit_garli_conf
    def edit_garli_conf(self, garli_conf, lines_to_edit, values_to_insert):

        """ {{{ Docstrings

        Returns a modified garli configuration file, given the original
        file, a list corresponding to the string values of the lines to be
        edited, and the values which are to be inserted.

        The values of 'lines_to_edit' and 'values_to_insert' arguments should
        be in corresponding order so that the first value of the former
        corresponds the the value you wish that parameter to have in the later.

        }}} """

        # Iterate through lines_to_edit and values_to_insert in tandem
        for i, j in zip(lines_to_edit, values_to_insert):
            # Append value
            garli_conf[garli_conf.index(i)] = '{0} {1}'.format(
                    garli_conf[garli_conf.index(i)], j
                    )
        return garli_conf
    # }}}

    # {{{ w_garli_conf
    def w_garli_conf(self, garli_conf):

        """ {{{ Docstrings

        Given the garli configuration file, read in a a list (utilizing the
        "readlines" function), modifies the garli.conf template file to
        reflect the paramters of the selected model as determined by
        jModelTest, utilizing edit_garli_conf, and writes it to a separate
        file.

        }}} """

        # Get the model selected
        model_selected = self._jMT_parameters['Model']
        # Check if model includes gamma distribution
        het = '+G' in model_selected
        # Check if model includes proportion of invariant sites
        inv = '+I' in model_selected
        # Remove these values; conflicts with Garli models dictionary
        model_selected = model_selected.translate(None, '+IG')
        # Variables in garli.conf to edit; see
        # https://molevol.mbl.edu/index.php/GARLI_Configuration_Settings
        # for explanation on pertinent variables
        # ::MODIFIABLE::
        # NOTE: If you would like to modify variables not currently
        # specified in garli_params, simply delete the value in the
        # template file so that the line appears as the others and add
        # the corresponding value, in the corresponding position, to
        # garli_values
        garli_variables = [
                'datafname =', 'ofprefix =', 'searchreps ='
                'bootstrapreps =', 'ratematrix =', 'statefrequencies =',
                'ratehetmodel =', 'numratecats =', 'invariantsites ='
                ]
        # Values of variables to insert
        garli_values = [
                self._path, self._identifier, str(args.np),
                str(args.bstr), Garli.models[str(model_selected)][0],
                Garli.models[str(model_selected)][1]
                ]
        # If model selected by jModelTest included gamma distribution, do so
        # in garli.conf
        if het:
            garli_values.extend(['gamma', '4'])
        # Else, don't
        else:
            garli_values.extend(['none', '1'])
        # If model selected by jModelTest included proportion invariant, do so
        # in garli.conf
        if inv:
            garli_values.append('estimate')
        # Else, don't
        else:
            garli_values.append('none')
        # Append values to respective variables
        garli_params = self.edit_garli_conf(
                garli_conf, garli_variables, garli_values
                )
        # Add newline "\n" character to end of every line
        garli_params = map(lambda x: x + '\n', garli_params)
        # Write modified garli.conf
        # Open in write mode
        with open(
                'garli_{0}.conf'.format(self._identifier), 'w'
                ) as garli_input:
            # Write lines
            for line in garli_params:
                garli_input.write(line)
    # }}}

    # {{{ run_garli
    def run_garli(self):

        """ {{{ Docstrings

        Run garli by spawning child process, utilizing "Popen" function
        provided by "subprocess" python module. The output/errors of this
        process are then subsequently printed, to stdout and written to a file,
        in real-time.

        }}} """

        # Specify child process, including any pertinent arguments
        # ::MODIFIABLE::
        # NOTE: You may have to change the manner in which garli is called,
        # depending on your system
        garli = 'mpirun garli -b -{0} garli_{1}.conf'.format(
                args.no_proc, self._identifier
                )
        # Spawn child process
        garli_run = Popen(
                garli.split(), stderr=STDOUT, stdout=PIPE, stdin=PIPE
                )
        # Open stdout of child process and print in real-time
        # Garli handles writing to file, unlike jModelTest
        for line in iter(garli_run.stdout.readline, ''):
            print(line.strip())
        # Close stdout
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

        """ {{{ Docstrings

        Add argument group "BEAST" to namespace and subsequent pertinent
        arguments to aforementioned group.

        }}} """

        args_BEAST = arg_parser.add_argument_group(
                'BEAST', 'Arguments for running BEAST module.'
                )
        args_BEAST.add_argument(
                  'BEAST', type=str, help='Path to beast.jar.'
                  )
        args_BEAST.add_argument(
                '--MCMC_BEAST', type=int, help=(
                        'Length of MCMC chain for BEAST analysis.'
                        ),
                default=50000000)
        args_BEAST.add_argument(
                '--burnin_BEAST', type=int, help=(
                        'Burnin for BEAST analysis.'
                        ),
                default=10000000)
        args_BEAST.add_argument(
                '--log_every', type=int, help=(
                        'Sample interval for BEAST analysis. This value will '
                        'be utilized to determine the frequency with which '
                        'the ".state" and ".trees" files are written to.'
                        ),
                default=1000)
        args_BEAST.add_argument(
                '-t', '--threshold', type=int, help=(
                        'Run script in threshold mode (i.e. BEAST will '
                        'continue to run, creating separate output directory '
                        'for each respective run, if after previous run, the '
                        'effective sample size did not meet this threshold).'
                        ),
                default=0)
        args_BEAST.add_argument(
                '--lcom', type=str, help=(
                        'Path to logcombiner. Only necessary if '
                        'running in threshold mode.')
                )
    # }}}

    # TODO(Edwin):
    # 1.) Add functions to __init__.
    # {{{ __init__
    def __init__(self):

        """ {{{ Docstrings

        Upon instantiating instance of class, run functions and store
        parameters.

        }}} """

        self._BEAST_XML = 'BEAST_{0}.xml'.format(self._identifier)
        self._BEAST_ID = 'BEAST_{0}.out'.format(self._identifier)
        self._beast_xml_tree, self._xml_ele_dict = self.parse_beast_xml()
        self.w_beast_submodel()
        self.w_beast_rates()
        self.w_beast_sequences()
    # }}}

    # {{{ parse_beast_xml
    @staticmethod
    def parse_beast_xml():

        """ {{{ Docstrings

        Parses BEAST XML input file utilizing "lxml" python module. Method is
        static because only necessary to run once; do not need to run upon
        every instantiation of BEAST class.

        }}} """

        # Initialize empty dictionary to store XML elements
        xml_ele_dict = {}
        # Set parser to automatically remove any impertinent whitespace as
        # well as any comments, respectively
        XML_parser = ET.XMLParser(remove_blank_text=True, remove_comments=True)
        # Parse BEAST XML input file template
        BEAST_XML = ET.parse('Standard.xml', XML_parser)
        # Get root of tree ('beast') element
        xml_ele_dict['root'] = BEAST_XML.getroot()
        # Get 'data' element where sequence information is stored
        xml_ele_dict['data'] = BEAST_XML.xpath('data')[0]
        # Get 'run' element where information pertaining to BEAST parameters
        # is stored
        xml_ele_dict['run'] = BEAST_XML.xpath('run')[0]
        # Get all pertinent subelements of run element
        for element in xml_ele_dict['run'].iter():
            if element.tag == 'state':
                xml_ele_dict['state'] = element
            if element.tag == 'substModel':
                xml_ele_dict['substmodel'] = element
            if element.tag == 'siteModel':
                xml_ele_dict['sitemodel'] = element
        for element in xml_ele_dict['sitemodel'].iter():
            if 'gammaShape.s:' in element.get('id'):
                xml_ele_dict['gamma'] = element
            if 'proportionInvariant.s:' in element.get('id'):
                xml_ele_dict['inv'] = element
        for element in xml_ele_dict['run'].iterfind('logger'):
            if 'treelog.t:' in element.get('id'):
                xml_ele_dict['tree_log'] = element
        return(BEAST_XML, xml_ele_dict)
    # }}}

    # {{{ JC_F81
    def JC_F81(self, xml_elements):

        """ {{{ Docstrings

        Function to handle setting of transition rates in BEAST XML input file
        for JC and F81 models given list of XML elements to edit.

        }}} """

        # Every transition rate is equal to "1.0"
        for i in xml_elements:
            i.text = '1.0'
    # }}}

    # {{{ K80_HKY
    def K80_HKY(self, xml_elements):

        """ {{{ Docstrings

        Function to handle setting of transition rates in BEAST XML input file
        for k80 and HKY models, given list of XML elements to edit.

        }}} """

        # Two distinct transition rates, one for transitions, the other for
        # transversions
        for i in xml_elements:
            if 'rateAG.s:' in i.get('id') or 'rateCT.s:' in i.get('id'):
                i.text = self._jMT_parameters['titv']
            else:
                i.text = '1.0'
    # }}}

    # {{{ calculate_ess
    def calculate_ess(self):

        """ {{{ Docstrings

        Calculates the effective sample size of data, given the name of the
        BEAST output file as a string, utilizing "genfromtxt" provided by the
        "numpy" python module and "acor" provided by the "acor" python module.

        }}} """

        # Read in data, ignoring comments, sample column, and header,
        # respectively
        data = genfromtxt(
                self._BEAST_ID, comments='#', usecols=range(1, 17)
                )[1:]
        # Concatenate data by columns
        data = zip(*data)
        # Calculate autocorrelation times (and other statistics) for each
        # column
        stats = map(lambda x: acor(x), data)
        # Extract autocorrelation times from statistics
        auto_cor_times = zip(*stats)[0]
        # Calculate MCMC chain length
        chain_length = int(args.MCMC_BEAST * (1 - args.burnin_BEAST))
        # Calculate effective sample size
        eff_sample_size = map(lambda x: chain_length / x, auto_cor_times)
        return eff_sample_size
    # }}}

    # {{{ w_beast_submodel
    def w_beast_submodel(self):

        """ {{{ Docstrings

        Writes parameters (i.e. gamma and proportion invariant) of model
        selected by jModelTest to BEAST XML.

        }}} """

        # Get the model selected
        model_selected = self._jMT_parameters['Model']
        # Check if model includes gamma distribution
        het = '+G' in model_selected
        # Check if model includes proportion invariant sites
        inv = '+I' in model_selected
        # Remove these values; conflicts with Garli models dictionary
        model_selected = model_selected.translate(None, '+IG')
        # If frequencies are estimated, do:
        # {{{ if estimate
        if Garli.models[str(model_selected)][1] == 'estimate':
            ET.SubElement(
                    self._xml_ele_dict['state'], 'parameter',
                    attrib={
                            'dimension': '4',
                            'id': 'freqParameter.s:{0}'.format(
                                    self._sequence_name
                                    ),
                            'lower': '0.0', 'name': 'stateNode',
                            'upper': '1.0'
                            }
                    ).text = '0.25'
            ET.SubElement(
                    self._xml_ele_dict['substmodel'], 'frequencies',
                    attrib={
                            'id': 'freqParameter.s:{0}'.format(
                                    self._sequence_name
                                    ),
                            'spec': 'Frequencies',
                            'frequencies': '@freqParameter.s:{0}'.format(
                                    self._sequence_name
                                    )
                            }
                    )
            freq_operator = ET.SubElement(
                    self._xml_ele_dict['run'], 'operator',
                    attrib={
                            'id': 'FrequenciesExchanger.s:{0}'.format(
                                    self._sequence_name
                                    ),
                            'spec': 'DeltaExchangeOperator',
                            'delta': '0.01',
                            'weight': '0.01'
                            }
                    )
            ET.SubElement(
                    freq_operator, 'parameter',
                    attrib={
                            'idref': 'freqParameter.s:{0}'.format(
                                    self._sequence_name
                                    )
                            }
                    )
            ET.SubElement(
                    self._xml_ele_dict['trace_log'], 'log',
                    attrib={
                            'idref': 'freqParameter.s:{0}'.format(
                                    self._sequence_name
                                    )
                            }
                    )
        # }}}
        # Else, if frequencies are equal, do:
        # {{{ elif equal
        elif Garli.models[str(model_selected)][1] == 'equal':
            ET.SubElement(
                    self._xml_ele_dict['substmodel'], 'frequencies',
                    attrib={
                            'id': 'equalFreqs.s:{0}'.format(
                                    self._sequence_name
                                    ),
                            'spec': 'Frequencies',
                            'data': '@{0}'.format(
                                    self._sequence_name
                                    ),
                            'estimate': 'false'
                            }
                    )
        # }}}
        # If model includes gamma distribution, do:
        if het:
            self._xml_ele_dict['sitemodel'].set('gammaCategoryCount', '4')
            self._xml_ele_dict['gamma'].text = self._jMT_parameters['gamma']
        # If model includes proportion of invariant sites, do:
        if inv:
            self._xml_ele_dict['inv'].text = self._jMT_parameters['pInv']
    # }}}

    # {{{ w_beast_rates
    def w_beast_rates(self):

        """ {{{ Docstrings

        Writes transition rates to BEAST XML.

        NOTE: The BEAST XML input file template, "Standard.xml" is configured
        to begin with a GTR model of DNA sequence evolution. This model is
        then "paired down" to reflect the model selected by jModelTest.

        }}} """

        # Initiate empty list to store pertinent XML elements
        xml_elements = []
        # Get the model selected by jModelTest, removing conflicting strings
        model_selected = self._jMT_parameters['Model'].translate(None, '+IG')
        # Iterate over subelements of the substmodel element, define each
        # respectively, and append to list
        for element in self._xml_ele_dict['substmodel'].iter():
            if 'rateAC.s:' in element.get('id'):
                rateAC = element
                xml_elements.append(element)
            if 'rateAG.s:' in element.get('id'):
                rateAG = element
                xml_elements.append(element)
            if 'rateAT.s:' in element.get('id'):
                rateAT = element
                xml_elements.append(element)
            if 'rateCG.s:' in element.get('id'):
                rateCG = element
                xml_elements.append(element)
            if 'rateCT.s:' in element.get('id'):
                rateCT = element
                xml_elements.append(element)
            if 'rateGT.s:' in element.get('id'):
                rateGT = element
                xml_elements.append(element)
        # If model selected is JC/F81 or K80/HKY,  pass xml_elements list to
        # respective function
        if model_selected == 'JC' or model_selected == 'F81':
            BEAST.JC_F81(self, xml_elements)
        elif model_selected == 'K80' or model_selected == 'HKY':
            BEAST.K80_HKY(self, xml_elements)
        # Else, set each rate individually
        else:
            rateAC.text = '%s' % self._jMT_parameters['Ra']
            rateAG.text = '%s' % self._jMT_parameters['Rb']
            rateAT.text = '%s' % self._jMT_parameters['Rc']
            rateCG.text = '%s' % self._jMT_parameters['Rd']
            rateCT.text = '%s' % self._jMT_parameters['Re']
            rateGT.text = '%s' % self._jMT_parameters['Rf']
    # }}}

    # {{{ get_sequence_range
    def get_sequence_range(self, nexus_file, start, end):

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

    # {{{ w_beast_sequences
    def w_beast_sequences(self, nexus_file):

        """ {{{ Docstrings

        Creates a subelement in the BEAST XML input file for each respective
        sequence, given a nexus file as a list and the 'data' XML element as an
        XML element.

        }}} """

        # Get start and end position of sequence block in nexus file
        sequence_start, sequence_end = self.get_sequence_range(
                nexus_file, 'matrix\n', ';\n'
                )
        # However, do not want to include these lines, just the lines between
        # them
        sequence_start += 1
        sequence_end -= 1
        # Iterate over lines in nexus file, defining each respective XML element
        for line in nexus_file:
            while sequence_start <= sequence_end:
                # Define variables for readability
                # Split line by occurrence of tab "\t" character
                line = nexus_file[int(sequence_start)].split('\t')
                # Get sequence ID
                sequence_id = line[0].strip()
                # Get sequence
                sequence = line[1].strip()
                # Create subelement
                ET.SubElement(
                        self._xml_ele_dict['data'], 'sequence',
                        attrib={
                                'id': 'seq_{0}'.format(sequence_id),
                                'taxon': '{0}'.format(sequence_id),
                                'totalcount': '4',
                                'value': '{0}'.format(sequence)
                        }
                )
                sequence_start += 1
    # }}}

    # {{{ w_beast_parameters
    def w_beast_parameters(self):

        """ {{{ Docstrings

        Finalizes parsing of the BEAST XML input file and writes the modifed
        ElementTree to a separate file given the BEAST XML input file as an
        ElementTree.

        }}} """

        # Set BEAST run parameters
        # Frequency with which to save to state file
        self._xml_ele_dict['state'].set('storeEvery', str(args.log_every))
        # MCMC chain length
        self._xml_ele_dict['run'].set('chainLength', str(args.MCMC_BEAST))
        # MCMC burnin
        self._xml_ele_dict['run'].set('preBurnin', str(args.burnin_BEAST))
        # Frequency with which to save to tree file
        self._xml_ele_dit['tree_log'].set('logEvery', '%s' % args.log_every)
        # Convert ElementTree to string in order to perform substitution
        beast_string = ET.tostring(beast_xml)
        # Substitute every occurrence of "replace_taxon" with
        # self._sequence_name
        beast_string = sub('replace_taxon', self._sequence_name, beast_xml)
        # Convert beast_string to file like object in order to re-parse it
        beast_file_obj = StringIO(beast_string)
        # Set parser to automatically remove any impertinent whitespace as
        # well as any comments, respectively
        XML_parser = ET.XMLParser(remove_blank_text=True, remove_comments=True)
        # Re-parse beast_file_obj into an ElementTree
        beast_xml = ET.parse(beast_file_obj, XML_parser)
        # Write beast_xml ElementTree to file, ensuring that it prints in a
        # human readable format and declaring pertinent XML parameters
        beast_xml.write(
                self._BEAST_XML, pretty_print=True, xml_declaration=True,
                encoding='UTF-8', standalone=False
                )
    # }}}

    # {{{ run_beast
    def run_beast(self):

        """ {{{ Docstrings

        Run BEAST by spawning child process, utilizing "Popen" function
        provided by "subprocess" python module. The output/errors of this
        process are then subsequently printed, to stdout and written to a file,
        in real-time.

        }}} """

        # Create directory; BEAST expects as such and will place output
        # in it
        os.mkdir(self._identifier)
        # Specify child process, including any pertinent arguments; see BEAST
        # documentation for explanation of additional arguments
        # ::MODIFIABLE::
        # NOTE: If you would like to modify arguments passed to BEAST,
        # simply format the following string in a matter of your choosing.
        # You may also have to change the manner in which BEAST is called,
        # depending on your system.
        beast = (
                'java -jar {0} -working -prefix {1} -seed {2} -threads {3} '
                '-beagle {4}'
                ).format(
                        args.BEAST, self._identifier,
                        randrange(0, 999999999999), args.no_proc,
                        self._BEAST_XML
                )
        # Spawn child process
        beast_run = Popen(
                beast.split(), stderr=STDOUT, stdout=PIPE,
                stdin=PIPE
                )
        # Open stdout of child process and print in real-time
        # BEAST handles writing to file, unlike jModelTest
        for line in iter(beast_run.stdout.readline, ''):
            print(line.strip())
        # Close stdout
        beast_run.stdout.close()
        # If user specified threshold in command line arguments, run
        # resume_beast
        if args.threshold:
            self.resume_beast()
    # }}}

    # {{{ resume_beast
    def resume_beast(self):

        """ {{{ Docstrings

        Continue to run BEAST in resume mode as long as any parameter in the
        BEAST output file does not meet the effective sample size threshold,
        creating a separate output directory for each run utilizing "Popen"
        function provided by "subprocess" python module. The output/errors of
        this process are then subsequently printed, to stdout and written to a
        file, in real-time.

        }}} """

        # Get current effective sample size
        effective_sample_size = self.calculate_ess()
        # Filter effective_sample_size to only include values less than the
        # threshold
        effective_sample_size = filter(
                lambda x: x < args.threshold, effective_sample_size
                )
        # While effective_sample_size does not equal an object of NoneType
        # (i.e. an empty list) BEAST will continue to run
        while effective_sample_size:
            # Specify child process, including any pertinent arguments
            # ::MODIFIABLE::
            # NOTE: See run_beast above.
            beast = (
                    'java -jar {0} -working -seed {1} -threads {2} -beagle '
                    '-resume -statefile {3}.xml.state {4}'
                    ).format(
                            args.BEAST, str(randrange(0, 999999999999)),
                            args.no_proc, self._sequence_name, self._BEAST_XML
                    )
            # Spawn child process
            beast_run = Popen(
                    beast.split(), stderr=STDOUT, stdout=PIPE,
                    stdin=PIPE
                    )
            # Open stdout of child process and print in real-time
            # BEAST handles writing to file, unlike jModelTest
            for line in iter(beast_run.stdout.readline, ''):
                print(line.strip())
            # Close stdout
            beast_run.stdout.close()
            # Get effective sample size after run
            effective_sample_size = self.calculate_ess()
            # Filter effective_sample_size to only include values greater than
            # the threshold; if none are, empty list of NoneType is returned
            effective_sample_size = filter(
                    lambda x: x < args.threshold, effective_sample_size
                    )
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
        args_nex.add_argument(
                '-np', '--no_proc', help=(
                        'When running script in HPC environment, specify '
                        'total number of processors requested so that the '
                        'script has knowledge of the environment and can '
                        'take full advantage of it.'
                        ),
                default=0
                )
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


# {{{ Define nexus files; batch
if args.batch:
    cwd = os.getcwd()
    files_in_dir = os.listdir(cwd)
    nexus_files = filter(lambda x: '.nex' in x, files_in_dir)
    for i in nexus_files:
        NexusFile(i)
else:
    nexus_files = []
    print('The program will prompt you for the path to each sequence file.')
    no_runs = raw_input('How many runs would you like to perform? ')
    for i in range(int(no_runs)):
        nexus_files.append(raw_input('Path to sequence file: '))
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
    if args.threshold:
        print('Threshold: %s' % args.threshold)
    print('Sample frequency BEAST: %s' % args.log_every)
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
    if args.threshold:
        sequence.resume_beast()
        sequence.log_combine()
    else:
        sequence.run_beast()
    sequence.clean_up()
    sequence.bGMYC(bGMYC_parameters)
# }}}
