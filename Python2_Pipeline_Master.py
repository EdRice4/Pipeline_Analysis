import os
from shutil import copy, move
from subprocess import Popen, STDOUT, PIPE
from lxml import etree as ET
from random import randrange
from numpy import loadtxt
import acor  # from acor import acor?
import argparse
import pyper


class CommonMethods(object):

    """Returns the range of user specified start and end sequences."""

    def get_range(self, range_file, start, end):
        range_start = range_file.index(start)
        range_file = range_file[range_start:]
        range_end = range_file.index(end) + range_start
        return range_start, range_end

    def filter_output(self, output, start, end):
        output = map(lambda x: x.translate(None, ' \r\n)'),
                     output[start:end])
        for num, i in enumerate(output):
            if '(ti/tv' in i:
                tmp = (output.pop(num)).split('(')
                output.insert(num, tmp[0])
                output.append(tmp[1])
        output = map(lambda x: x.translate(None, '('), output)
        return output

    def dict_check(self, string, dict):
        if string in dict:
            return dict[string]
        else:
            return 'None.'

    def file_edit(self, file_to_edit, lines_to_edit, values_to_insert):
        lines = []
        for num, i in enumerate(file_to_edit):
            if i.strip() in lines_to_edit:
                    lines.append(num)
            tmpl = map(lambda x, y: x + ' ' + y + '\n', lines_to_edit,
                       values_to_insert)
            tmpd = dict(zip(tmpl, lines))
            for i in tmpd:
                file_to_edit[tmpd[i]] = i
        return file_to_edit


class jModelTest(CommonMethods):

    """Run jModelTest and store parameters associated with output."""

    def run_jModelTest(self):
        jModelTest = 'java -jar %s -d %s -t fixed -s 11 -i -g 4 -f -tr 1' % (
                     args.jMT, self.path)
        jMT_run = Popen(jModelTest.split(), stderr=STDOUT, stdout=PIPE,
                        universal_newlines=True)
        with open(self.JMT_ID, 'w') as output:
            for line in iter(jMT_run.stdout.readline, ''):
                print(line.strip())
                output.write(str(line))
            jMT_run.stdout.close()

    def r_jModelTest_parameters(self, jModelTest_file):
        start, end = self.get_range(jModelTest_file, ' Model selected: \n',
                                    ' \n')
        data = self.filter_output(jModelTest_file, start + 1, end)
        for i in data:
            self.parameters[i.rpartition('=')[0]] = i.rpartition('=')[-1]


class Garli(jModelTest):

    """Run garli and store parameters associated with output."""

    models = {
        'JC': ['1rate', 'equal'],
        'F81': ['1rate', 'estimate'],
        'K80': ['2rate', 'equal'],
        'HKY': ['2rate', 'estimate'],
        'TrNef': ['0 1 0 0 2 0', 'equal'],
        'TrN': ['0 1 0 0 2 0', 'estimate'],
        'TPM1': ['0 1 2 2 1 0', 'equal'],
        'TPM1uf': ['0 1 2 2 1 0', 'estimate'],
        'TPM2': ['0 1 0 2 1 2', 'equal'],
        'TPM2uf': ['0 1 0 2 1 2', 'estimate'],
        'TPM3': ['0 1 2 0 1 2', 'equal'],
        'TPM3uf': ['0 1 2 0 1 2', 'estimate'],
        'K3P': ['0 1 2 2 1 0', 'equal'],
        'K3Puf': ['0 1 2 2 1 0', 'estimate'],
        'TM1ef': ['0 1 2 2 3 0', 'equal'],  # Remove 'I' for translate.
        'TM1': ['0 1 2 2 3 0', 'estimate'],  # Remove 'I' for translate.
        'TM2ef': ['0 1 0 2 3 2', 'equal'],
        'TM2': ['(0 1 0 2 3 2)', 'estimate'],
        'TM3ef': ['0 1 2 0 3 2', 'equal'],
        'TM3': ['0 1 2 0 3 2', 'estimate'],
        'TVMef': ['0 1 2 3 1 4', 'equal'],
        'TVM': ['0 1 2 3 1 4', 'estimate'],
        'SYM': ['6rate', 'equal'],
        'GTR': ['6rate', 'estimate']
    }

    def w_garli_conf(self, garli_file):
        model_selected = self.parameters['Model']
        het = '+G' in model_selected
        inv = '+I' in model_selected
        model_selected = model_selected.translate(None, '+IG')
        garli_params = ['datafname =', 'ofprefix =',
                        'bootstrapreps =', 'ratematrix =',
                        'statefrequencies =', 'ratehetmodel =',
                        'numratecats =', 'invariantsites =']
        garli_values = [self.path, self.identifier, str(args.bootstrap),
                        Garli.models[str(model_selected)][0],
                        Garli.models[str(model_selected)][1]]
        if het:
            garli_values.extend(['gamma', '4'])
        else:
            garli_values.extend(['none', '1'])
        if inv:
            garli_values.append('estimate')
        else:
            garli_values.append('none')
        garli_file = self.file_edit(garli_file, garli_params, garli_values)
        with open('garli_%s.conf' % self.identifier, 'w+') as garli_output:
            for i in garli_file:
                garli_output.write(i)

    def run_garli(self):
        garli = './Garli -b garli_%s.conf' % self.identifier
        garli_run = Popen(garli.split(), stderr=STDOUT, stdout=PIPE,
                          stdin=PIPE)
        for line in iter(garli_run.stdout.readline, ''):
            print(line.strip())
        garli_run.stdout.close()


class ToleranceCheck(Garli):

    """A class that can calculate statistics of data in a file separated into
       columns."""

    def calculate_statistics(self, data_file, rows, cols):
        data = loadtxt(self.BEAST_ID, unpack=True, skiprows=rows, usecols=cols)
        auto_cor_times = zip(*(map(lambda x: acor.acor(x), data)))[0]
        eff_sample_size = map(lambda x, y: x/(len(y)), data, auto_cor_times)
        return eff_sample_size


class BEAST(ToleranceCheck):

    """Run BEAST and store parameters associated with output."""

    def JC_F81(self, *xml_nodes):
        for i in xml_nodes:
            i.text = '1.0'

    def K80_HKY(self, *xml_nodes):
        for i in xml_nodes:
            if i == rateAG or i == rateCT:
                i.text = self.parameters['ti/tv']
            else:
                i.text = '1.0'

    sub_models = {'JC': JC_F81, 'F81': JC_F81,
                  'K80': K80_HKY, 'HKY': K80_HKY}

    def w_beast_submodel(self):
        model_selected = self.parameters['Model']
        het = '+G' in model_selected
        inv = '+I' in model_selected
        model_selected = model_selected.translate(None, '+IG')
        run.set('chainLength', '%s' % args.MCMC_BEAST)
        run.set('preBurnin', '%s' % args.burnin_BEAST)
        log.set('logEvery', '%s' % args.store_every)
        screen_log.set('logEvery', '%s' % args.store_every)
        tree_log.set('logEvery', '%s' % args.store_every)
        if Garli.models[str(model_selected)][1] == 'estimate':
            freq = ET.SubElement(state, 'parameter', attrib={
                                 'dimension': '4',
                                 'id': 'freqParameter.s:%s' % self.sequence_name,
                                 'lower': '0.0', 'name': 'stateNode',
                                 'upper': '1.0'})
            freq.text = '0.25'
            freq_log = ET.SubElement(log, 'parameter', attrib={
                                     'idref': 'freqParameter.s:%s' % self.sequence_name,
                                     'name': 'log'})
        if Garli.models[str(model_selected)][1] == 'equal':
            freq = ET.SubElement(substmodel, 'frequencies', attrib={
                                 'data': '@%s' % self.sequence_name,
                                 'estimate': 'false',
                                 'id': 'equalFreqs.s:%s' % self.sequence_name,
                                 'spec': 'Frequencies'})
        if het:
            sitemodel.set('gammaCategoryCount', '4')
            gamma_shape = ET.SubElement(sitemodel, 'parameter', attrib={
                                        'estimate': 'false', 'id': 'gammaShape.s:%s' % self.sequence_name,
                                        'name': 'shape'})
            gamma_shape.text = self.parameters['gammashape']
        if inv:
            p_inv = ET.SubElement(siteModel, 'parameter', attrib={
                                  'estimate': 'false',
                                  'id': 'proportionInvaraint.s:%s' % self.sequence_name,
                                  'lower': '0.0', 'name': 'proportionInvaraint',
                                  'upper': '1.0'})
            p_inv.text = self.parameters['p-inv']

    # May be able to consolidate this.
    def w_beast_rates(self):
        xml_nodes = []
        model_selected = (self.parameters['Model']).translate(None, '+IG')
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
        if self.dict_check(str(model_selected), BEAST.sub_models) != 'None.':
            BEAST.sub_models[str(model_selected)](xml_nodes)
        else:
            rateAC.text = '%s' % self.parameters['Ra[AC]']
            rateAG.text = '%s' % self.parameters['Rb[AG]']
            rateAT.text = '%s' % self.parameters['Rc[AT]']
            rateCG.text = '%s' % self.parameters['Rd[CG]']
            rateCT.text = '%s' % self.parameters['Re[CT]']
            rateGT.text = '%s' % self.parameters['Rf[GT]']

    def w_beast_taxon(self):
        sequence_start, sequence_end = self.get_range(self.nexus_file,
                                                      '\tmatrix\r\n', '\r\n')
        sequence_start += 1
        sequence_end -= 1
        for line in self.nexus_file:
            while sequence_start <= sequence_end:
                species_id = (self.nexus_file[int(sequence_start)].rpartition(
                              "\t")[0]).strip()
                species_sequence = (self.nexus_file[int(sequence_start)].rpartition("\t")[-1]).strip()
                sequence = ET.SubElement(data, 'sequence', attrib={
                                         'id': 'seq_%s' % species_id,
                                         'taxon': '%s' % species_id,
                                         'totalcount': '4',
                                         'value': '%s' % species_sequence})
                sequence_start += 1

    def beast_finalize(self):
        log.set('fileName', str(self.BEAST_ID))
        beast.write(self.BEAST_XML, pretty_print=True, xml_declaration=True, encoding='UTF-8', standalone=False)
        with open(self.BEAST_XML, 'r+') as beast_xml_file:
            beast_xml = beast_xml_file.readlines()
        for num, item in enumerate(beast_xml):
            item = item.replace('replace_taxon', str(self.sequence_name))
            beast_xml[num] = item
        with open(self.BEAST_XML, 'w') as beast_xml_file:
            beast_xml_file.write(''.join(beast_xml))

    def run_beast(self):
        BEAST = 'java -jar %s -prefix %s -seed %s %s' % (args.BEAST,
                                                         self.identifier,
                                                         str(randrange(0, 999999)),
                                                         self.BEAST_XML)
        beast_run = Popen(BEAST.split(), stderr=STDOUT, stdout=PIPE, stdin=PIPE)
        for line in iter(beast_run.stdout.readline, ''):
            print(line.strip())
        beast_run.stdout.close()

    def resume_beast(self, BEAST_log_file):
        delimiter = ('Sample\tposterior\tlikelihood\tprior'
                     '\ttreeLikelihood\tTreeHeight\tYuleModel'
                     '\tbirthRate\tmutationRate\tfreqParameter.1'
                     '\tfreqParameter.2\tfreqParameter.3\t'
                     'freqParameter.4\tfreqParameter.1\t'
                     'freqParameter.2\tfreqParameter.3 \t'
                     'freqParameter.4\t\n')
        rows = data_file.index(delimiter) + 1
        cols = range(1, 16)
        eff_sample_size = self.calculate_statistics(BEAST_log_file, rows, cols)
        eff_sample_size = filter(lambda x: x < args.tolerance, eff_sample_size)
        run_number = 1
        if eff_sample_size:
            os.rename('%s.trees' % self.sequence_name, '%s_%s.trees.bu' % (self.sequence_name, run_number))
            BEAST = 'java -jar ../%s -resume -seed %s ../%s' % (args.BEAST,
                                                                str(randrange(0, 999999)),
                                                                self.BEAST_XML)
            beast_run = Popen(BEAST.split(), stderr=STDOUT, stdout=PIPE,
                              stdin=PIPE)
            for line in iter(beast_run.stdout.readline, ''):
                print(line.strip())
            beast_run.stdout.close()
            run_number += 1
            self.resume_beast(BEAST_log_file)


class bGMYC(BEAST):

    """A class used to run bGMYC in R with pypeR module."""

    def bGMYC(self):
        os.chdir(str(self.identifier))
        threshold = int(round((args.t1 + args.t2) / 2))
        r = pyper.R()
        r("library(ape)")
        r("library(bGMYC)")
        r("read.nexus(file='%s.trees') -> trees" % self.sequence_name)
        r("bgmyc.multiphylo(trees, mcmc=%i, burnin=%i, thinning=%i, t1=%i, "
          "t2=%i, start=c(1,1,%i)) -> result.multi" % (args.MCMC_bGMYC,
                                                       args.burnin_bGMYC,
                                                       args.thinning,
                                                       args.t1, args.t2,
                                                       threshold))
        r("svg('%s_mcmc.svg')" % self.identifier)
        r("plot(result.multi)")
        r("dev.off()")
        r('bgmyc.spec(result.multi, filename="%s.txt") -> result.spec' % self.identifier)
        r('spec.probmat(result.multi) -> result.probmat')
        r('svg("%s_prob.svg")' % self.identifier)
        r('plot(result.probmat, trees[[1]])')
        r('dev.off()')


class CleanUp(bGMYC):

    """A class used to consolidate all output in run."""

    def clean_up(self):
        cwd = os.getcwd()
        files_in_dir = os.listdir(cwd)
        output_files = filter(lambda x: self.identifier in x, files_in_dir)
        for i in output_files:
            move(i, self.identifier)
        copy(self.path, self.identifier)


class IterRegistry(type):

    """A metaclass to allow for iteration over instances of NexusFile class."""

    def __iter__(cls):
        return iter(cls.registry)


class NexusFile(CleanUp):

    """A class in which we will store the parameters associated with the
       given nexus file."""

    __metaclass__ = IterRegistry
    registry = []

    def __init__(self, seq_name, path, seq_file):
        self.path = str(path)
        self.sequence_name = self.path.strip('.nex')
        self.nexus_file = seq_file.readlines()
        self.identifier = str(seq_name) + '_' + str(randrange(0, 999999999))
        self.JMT_ID = 'jModelTest_%s.out' % self.identifier
        self.parameters = {}
        self.BEAST_XML = 'BEAST_%s.xml' % self.identifier
        self.BEAST_ID = 'BEAST_%s.out' % self.identifier
        self.registry.append(self)

arg_parser = argparse.ArgumentParser()
arg_parser.add_argument('jMT', type=str, help='path to jModelTest.jar')
arg_parser.add_argument('BEAST', type=str, help='path to beast.jar')
arg_parser.add_argument('-b', '--batch', help=('run script in batch mode '
                        'for multiple nexus files'), action='store_true')
arg_parser.add_argument('-g', '--garli', help=('run garli analysis prior to '
                        'BEAST'), action='store_true')
arg_parser.add_argument('-bsr', '--bootstrap', type=int, help=('# of bootstrap'
                        ' replications for garli analysis'))
arg_parser.add_argument('MCMC_BEAST', type=int, help=('length of MCMC chain '
                        'for BEAST analysis'))
arg_parser.add_argument('store_every', type=int, help=('sample interval '
                        'for BEAST analysis'))
arg_parser.add_argument('-t', '--tolerance', help=('run script in tolerance '
                        'mode for BEAST run'), action='store_true')
arg_parser.add_argument('--tol_value', type=int, help=('value of toelrance '
                        'for BEAST run'))
arg_parser.add_argument('--burnin_BEAST', type=int, help=('burnin for BEAST '
                        'run default = 0.25 of chain length'))
arg_parser.add_argument('MCMC_bGMYC', type=int, help=('length of MCM chain '
                        'for bGMYC analysis'))
arg_parser.add_argument('--burnin_bGMYC', type=int, help=('burnin for bGMYC '
                        'run default = 0.25 of chain length'))
arg_parser.add_argument('thinning', type=int, help=('sample interval for '
                        ' bGMYC analysis'))
arg_parser.add_argument('t1', type=int, help=('value of t1 for bGMYC analysis '
                        'see instructions in bGMYC documentation'))
arg_parser.add_argument('t2', type=int, help=('value of t1 for bGMYC analysis '
                        'see instructions in bGMYC documentation'))
args = arg_parser.parse_args()

if not args.tol_value:
    args.tol_value = 100
if not args.burnin_BEAST:
    args.burnin_BEAST = int(round(args.MCMC_BEAST * 0.25))
if not args.burnin_bGMYC:
    args.burnin_bGMYC = int(round(args.MCMC_bGMYC * 0.25))

XML_parser = ET.XMLParser(remove_blank_text=True)
beast = ET.parse('Standard.xml', XML_parser)
data = beast.find('data')
run = beast.find('run')
for element in run.iter():
    if element.tag == 'state':
        state = element
    if element.tag == 'substModel':
        substmodel = element
        sitemodel = element
for element in run.iterfind('logger'):
    if element.get('id') == 'tracelog':
        log = element
    if element.get('id') == 'screenlog':
        screen_log = element
    if 'treelog.t:' in element.get('id'):
        tree_log = element

path_to_sequence = {}

if args.batch:
    cwd = os.getcwd()
    files_in_dir = os.listdir(cwd)
    nexus_files = filter(lambda x: '.nex' in x, files_in_dir)
    for i in nexus_files:
        path = i
        class_name = i.strip('.nex')
        path_to_sequence[str(class_name)] = str(path)
else:
    print ('The program will prompt you for the path to each sequence file ' +
           'as well as a unique name for each instantiated class.')
    no_runs = raw_input('How many runs would you like to perform? ')
    for i in range(int(no_runs)):
        path = raw_input('Path to sequence: ')
        class_name = raw_input('Name of class: ')
        path_to_sequence[str(class_name)] = str(path)

for key in path_to_sequence:
    with open(str(path_to_sequence[key]), 'r') as sequence_file:
        NexusFile(key, path_to_sequence[key], sequence_file)

for sequence in NexusFile:
    print('-----------------------------------------------------------------')
    print('Sequence file: %s' % sequence.path)
    print('Run identifier: %s' % sequence.identifier)
    print('Garli bootstrap replications: %s' % args.bootstrap)
    print('Length of MCMC chain: %s' % args.MCMC_BEAST)
    print('Sample frequency: %s' % args.store_every)
    print('Burnin: %s' % args.burnin_BEAST)
    if args.tolerance:
        print('Tolerance: %s' % args.tol_value)
    print('-----------------------------------------------------------------')
    sequence.run_jModelTest()
    with open(str(sequence.JMT_ID), 'r') as JMT_output:
        JMT_output = JMT_output.readlines()
    sequence.r_jModelTest_parameters(JMT_output)
    for keys, values in sequence.parameters.items():
        print(keys)
        print(values)
    #if args.garli:
        #with open('garli.conf', 'r') as garli_conf:
            #garli_conf = garli_conf.readlines()
        #sequence.w_garli_conf(garli_conf)
        #sequence.run_garli()
    #sequence.w_beast_submodel()
    #sequence.w_beast_rates()
    #sequence.w_beast_taxon()
    #sequence.beast_finalize()
    #os.mkdir(str(sequence.identifier))
    #sequence.run_beast()
    #if args.tolerance:
        #os.chdir(str(sequence.identifier))
        #with open(str(sequence.BEAST_ID), 'r') as data_file:
                #data_file = data_file.readlines()
        #sequence.resume_beast(data_file)
        #os.chdir('..')
    #sequence.clean_up()
    #sequence.bGMYC()
