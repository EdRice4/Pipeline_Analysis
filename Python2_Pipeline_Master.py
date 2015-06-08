from subprocess import Popen, STDOUT, PIPE
from lxml import etree as ET
from random import randrange
from numpy import genfromtxt
from acor import acor
from re import sub
from shutil import move, copy
import argparse
import os


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
                if line != 'Cannot perform output.\n':
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

    def calculate_statistics(self, data_file):
        data = (genfromtxt(data_file, comments='#', usecols=range(1, 17)))[1:]
        data = zip(*data)
        stats = map(lambda x: acor(x), data)
        auto_cor_times = (zip(*stats))[0]
        chain_length = args.MCMC_BEAST - args.burnin_BEAST
        eff_sample_size = map(lambda x: chain_length/x, auto_cor_times)
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
        run.set('preBurnin', '0')
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
                                        'estimate': 'false',
                                        'id': 'gammaShape.s:%s' % self.sequence_name,
                                        'name': 'shape'})
            gamma_shape.text = self.parameters['gammashape']
        else:
            gamma_shape = ET.SubElement(sitemodel, 'parameter', attrib={
                                        'estimate': 'false',
                                        'id': 'gammaShape.s:%s' % self.sequence_name,
                                        'name': 'shape'})
            gamma_shape.text = '0.0'
        if inv:
            p_inv = ET.SubElement(sitemodel, 'parameter', attrib={
                                  'estimate': 'false',
                                  'id': 'proportionInvariant.s:%s' % self.sequence_name,
                                  'lower': '0.0', 'name': 'proportionInvariant',
                                  'upper': '1.0'})
            p_inv.text = self.parameters['p-inv']
        else:
            p_inv = ET.SubElement(sitemodel, 'parameter', attrib={
                                  'estimate': 'false',
                                  'id': 'proportionInvariant.s:%s' % self.sequence_name,
                                  'lower': '0.0', 'name': 'proportionInvariant',
                                  'upper': '1.0'})
            p_inv.text = '0.0'

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
                                                      'matrix\n', ';\n')
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
        log.set('fileName', self.BEAST_ID)
        beast.write(self.BEAST_XML, pretty_print=True, xml_declaration=True,
                    encoding='UTF-8', standalone=False)
        with open(self.BEAST_XML, 'r+') as beast_xml_file:
            beast_xml = beast_xml_file.read()
        beast_xml = sub('replace_taxon', self.sequence_name, beast_xml)
        with open(self.BEAST_XML, 'w') as beast_xml_file:
            beast_xml_file.write(beast_xml)

    def run_beast(self):
        os.mkdir(self.identifier)
        BEAST = '%s -prefix %s -seed %s %s' % (args.BEAST, self.identifier,
                                               str(randrange(0, 999999)),
                                               self.BEAST_XML)
        beast_run = Popen(BEAST.split(), stderr=STDOUT, stdout=PIPE,
                          stdin=PIPE)
        for line in iter(beast_run.stdout.readline, ''):
            print(line.strip())
        beast_run.stdout.close()

    def resume_beast(self, BEAST_log_file):
        ess = 1
        run_count = 1
        while ess:
            run = self.identifier + '_RUN_' + str(run_count)
            os.mkdir(run)
            BEAST = '%s -prefix %s -seed %s %s' % (args.BEAST, run,
                                                   randrange(0, 999999999),
                                                   self.BEAST_XML)
            beast_run = Popen(BEAST.split(), stderr=STDOUT, stdout=PIPE,
                              stdin=PIPE)
            for line in iter(beast_run.stdout.readline, ''):
                print(line.strip())
            beast_run.stdout.close()
            run_count += 1
            ess = self.calculate_statistics(run + '/' + BEAST_log_file)
            ess = filter(lambda x: x < args.tolerance, ess)

    def log_combine(self):
        cwd = os.getcwd()
        fid = os.listdir(cwd)
        burnin_perc = int(args.burnin_BEAST / args.MCMC_BEAST)
        bdirs = filter(lambda x: '_RUN_' in x, fid)
        if len(bdirs) > 1:
            bdirs = map(lambda x: '-log ' + x + '/' + self.BEAST_ID, bdirs)
            com = './%s %s -b %s -o MASTER_%s' % (args.lcom,
                                                  ' '.join(bdirs),
                                                  burnin_perc,
                                                  self.BEAST_ID)
            lcom = Popen(com.split(), stderr=STDOUT, stdout=PIPE, stdin=PIPE)
            for line in iter(lcom.stdout.readline, ''):
                print(line.strip())
            lcom.stdout.close()


class bGMYC(BEAST):

    """A class used to run bGMYC in R with pypeR module."""

    def bGMYC(self):
        threshold = round((args.t1 + args.t2) / 2)
        parameters = [self.sequence_name, self.identifier, args.MCMC_bGMYC,
                      args.burnin_bGMYC, args.thinning, args.t1, args.t2,
                      threshold]
        parameters = map(lambda x: str(x), parameters)
        os.chdir(self.master_dir)
        cwd = os.getcwd()  # required?
        fid = os.listdir(cwd)
        bdirs = filter(lambda x: '_RUN_' in x, fid)
        for i in bdirs:
            os.chdir(i)
            Rscript = 'Rscript --save ../../bGMYC.R %s' % ' '.join(parameters)
            bGMYC_run = Popen(Rscript.split(), stderr=STDOUT, stdout=PIPE,
                              stdin=PIPE)
            for line in iter(bGMYC_run.stdout.readline, ''):
                print(line.strip())
            bGMYC_run.stdout.close()
            os.chdir('../')


class CleanUp(bGMYC):

    """A class used to consolidate all output in run."""

    def clean_up(self):
        cwd = os.getcwd()
        files_in_dir = os.listdir(cwd)
        output_files = filter(lambda x: self.identifier in x, files_in_dir)
        os.mkdir(self.master_dir)
        for i in output_files:
            move(i, self.master_dir)
        copy(self.path, self.master_dir)


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
        self.sequence_name = self.path.replace('.nex', '')
        self.nexus_file = seq_file.readlines()
        self.identifier = seq_name + '_' + str(randrange(0, 999999999))
        self.JMT_ID = 'jModelTest_%s.out' % self.identifier
        self.parameters = {}
        self.BEAST_XML = 'BEAST_%s.xml' % self.identifier
        self.BEAST_ID = 'BEAST_%s.out' % self.identifier
        self.master_dir = self.identifier + '_MASTER'
        self.registry.append(self)

arg_parser = argparse.ArgumentParser(
        prog='Pipeline',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description=('A pipeline between jModelTest, Garli, BEAST and bGMYC.'))
arg_parser.add_argument(
        'jMT', type=str, help='Path to jModelTest.jar.')
arg_parser.add_argument(
        'BEAST', type=str, help='Path to beast.jar.')
arg_parser.add_argument(
        '-b', '--batch', help=('Run script in batch mode for multiple nexus '
                               'files.'),
        action='store_true')
arg_parser.add_argument('-g', '--garli', help=('Run garli analysis prior to '
                                               'BEAST.'),
                        action='store_true')
arg_parser.add_argument('-bsr', '--bootstrap', type=int, help=('# of bootstrap'
                                                               ' replications'
                                                               ' for garli '
                                                               'analysis.'),
                        action='store_true')
arg_parser.add_argument('MCMC_BEAST', type=int, help=('Length of MCMC chain '
                                                      'for BEAST analysis.'))
arg_parser.add_argument('store_every', type=int, help=('Sample interval '
                                                       'for BEAST analysis.'))
arg_parser.add_argument('-t', '--tolerance', help=('Run script in tolerance '
                                                   'mode for BEAST run.'),
                        action='store_true')
arg_parser.add_argument('--tol_value', type=int, help=('Value of toelrance '
                        'for BEAST run.'))
arg_parser.add_argument('--lcom', type=str, help=('Path to logcombiner. Only '
                        'necessary if running in tolerance mode.'))
arg_parser.add_argument('--burnin_BEAST', type=int, help=('Burnin for BEAST '
                        'run default = 0.25 of chain length.'))
arg_parser.add_argument('MCMC_bGMYC', type=int, help=('Length of MCMC chain '
                        'for bGMYC analysis.'))
arg_parser.add_argument('--burnin_bGMYC', type=int, help=('Burnin for bGMYC '
                        'run default = 0.25 of chain length.'))
arg_parser.add_argument('thinning', type=int, help=('Sample interval for '
                        ' bGMYC analysis.'))
arg_parser.add_argument('t1', type=int, help=('Value of t1 for bGMYC analysis '
                        'see instructions in bGMYC documentation.'))
arg_parser.add_argument('t2', type=int, help=('Value of t1 for bGMYC analysis '
                        'see instructions in bGMYC documentation.'))
args = arg_parser.parse_args()

if not args.bootstrap:
    args.bootstrap = 0
if args.tolerance and not args.tol_value:
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
    if element.tag == 'siteModel':
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
    with open(path_to_sequence[key], 'r') as sequence_file:
        NexusFile(key, path_to_sequence[key], sequence_file)

for sequence in NexusFile:
    print('-----------------------------------------------------------------')
    print('Sequence file: %s' % sequence.path)
    print('Run identifier: %s' % sequence.identifier)
    #print('Garli bootstrap replications: %s' % args.bootstrap)
    print('MCMC BEAST: %s' % args.MCMC_BEAST)
    print('Burnin BEAST: %s' % args.burnin_BEAST)
    if args.tolerance:
        print('Tolerance: %s' % args.tol_value)
    print('Sample frequency BEAST: %s' % args.store_every)
    print('MCMC bGMYC: %s' % args.MCMC_bGMYC)
    print('Burnin bGMYC: %s' % args.burnin_bGMYC)
    print('Sample frequency bGMYC: %s' % args.thinning)
    print('-----------------------------------------------------------------')
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
        sequence.resume_beast(sequence.BEAST_ID)
        sequence.log_combine()
    else:
        sequence.run_beast()
    sequence.clean_up()
    sequence.bGMYC()
