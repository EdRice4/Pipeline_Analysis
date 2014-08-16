from lxml import etree as ET

def w_beast_submodel(self, beast_xml):
    parameters = self.parameters
    model_selected = parameters[0][1]
    taxon = self.sequence_name
    het = '+G' in model_selected
    inv = '+I' in model_selected
    beast = ET.parse('BEAST_FreqEq.xml')
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
        if element.get('id') == 'treelog.t:%s': % taxon
            tree_log = element
    # Need to write to XML?
    run.set('chainLength', '%s' % chain_length)
    run.set('preBurnin', '%s' % burnin)
    log.set('logEvery', '%s' store_every)
    screen_log.set('logEvery', '%s' store_every)
    tree_log.set('logEvery', '%s' store_every)
    if Garli.models[str(model_selected)][1] == 'estimate':
        freq = ET.SubElement(state, 'parameter', attrib = {
                             'dimension' : '4', 
                             'id' : 'freqParameter.s:%s', % taxon
                             'lower' : '0.0', 'name' : 'stateNode',
                             'upper' : '1.0'})
        freq.text = '0.25'
        freq_log = log.SubElement(log, 'parameter', attrib = {
                                  'idref' : 'freqParameter.s:%s' % taxon
                                  'name' : 'log'})
    if Garli.models[str(model_selected)][1] == 'equal':
        freq = ET.SubElement(substmodel, 'frequencies', attrib = {
                             'data' : '@%s', % taxon 'estimate' : 'false',
                             'id' : 'equalFreqs.s:%s', % taxon
                             'spec' : 'Frequencies'})
    if het == True:
        sitemodel.set('gammaCategoryCount', '4')
        gamma_shape = ET.SubElement(sitemodel, 'parameter', attrib = {
                      'estimate' : 'false', 'id' : 'gammaShape.s:%s', % taxon
                      'name' : 'shape'})
        gamma_shape.text = parameters['gammashape']
    if inv == True:
        p_inv = ET.SubElement(siteModel, 'parameter', attrib = {
                              'estimate' : 'false', 
                              'id' : 'proportionInvaraint.s:%s', % taxon
                              'lower' : '0.0', 'name' : 'proportionInvaraint'
                              'upper' : '1.0'})
        p_inv.text = parameters['p-inv']

def dict_check(string, dict):
    if string in dict:
        return dict[string]
    else:
        return 'None.'

def w_beast_rates(self, beast_xml):

    sub_models = {'JC' : JC_F81, 'F81' : JC_F81,
                  'K80' : 'K80_HKY', 'HKY' : 'K80_HKY'}

    parameters = self.parameters
    model = (parameters['Model']).translate(None, '+IG')
    for element in substmodel.iter():
        if element.get('id') == 'rateAC.s:%s': % taxon
            rateAC = element
        if element.get('id') == 'rateAG.s:%s': % taxon
            rateAG = element
        if element.get('id') == 'rateAT.s:%s': % taxon
            rateAT = element
        if element.get('id') == 'rateCG.s:%s': % taxon
            rateCG = element
        if element.get('id') == 'rateCT.s:%s': % taxon
            rateCT = element
        if element.get('id') == 'rateGT.s:%s': % taxon
            rateGT = element
    if dict_check(parameters['Model'], sub_models) != 'None.':
        sub_models[model](xml_nodes)
    else:
        rateAC.text = '%s' % parameters['R(a)[AC]']
        rateAG.text = '%s' % parameters['R(b)[AG]']
        rateAT.text = '%s' % parameters['R(c)[AT]']
        rateCG.text = '%s' % parameters['R(d)[CG]']
        rateCT.text = '%s' % parameters['R(e)[CT]']
        rateGT.text = '%s' % parameters['R(f)[GT]']

def JC_F81(self, *xml_nodes):
    for i in xml_nodes:
        i.text = '1.0'

def K80_HKY(self, *xml_nodoes):
    self.parameters = parameters
    for i in xml_nodes:
        if i == rateAG or i == rateCT:
            i.text = parameters['ti/tv']
        else:
            i.text = '1.0'

sub_models = {'JC' : JC_F81, 'F81' : JC_F81, 'K80' : 'K80_HKY', 'HKY' : 'K80_HKY']
else:


def identify_taxon_and_seq(self, seq_file, beast_xml):
        sequence_start, sequence_end = self.get_range(self, self.seq_file, '\tmatrix\n',
                                                 '\n')
        sequence_start += 1
        seq_file = seq_file.readlines()
        for line in seq_file:
            while sequence_start <= sequence_end:
                species_id = getline(str(path_to_sequence), int(sequence_start)).rpartition("\t")[0]
                species_sequence = getline(str(path_to_sequence), int(sequence_start)).rpartition("\t")[-1]
                data = root.find('data')
                sequence = ET.Element('sequence', id='%s' % species_id,
                                      taxon='%s' % species_id, totalcount='4',
                                      value='%s' % species_sequence)
                data.append(sequence)
                output.write('Standard_%s_.xml' % sequence_name)

for num, item in enumerate(beast_xml):
    if het == True:
    if inv == True:
    item = item.replace('PUT_NAME_OF_FILE_SANS_NEX_HERE', str(self.sequence_name))
    beast_xml[num] = item
beast_xml = ET.XML((''.join(beast_xml)))
output.write(ET.tostring(beast_xml, pretty_print = True))

rates = ['rateAC.s:%s', 'rateAG.s:%s', 'rateAT.s:%s', 'rateCG.s:%s'
         'rateGT.s:%s']