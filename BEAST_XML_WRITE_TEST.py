from random import randrange
# from xml.dom import minidom
# import xml.etree.ElementTree as ET
from lxml import etree as ET

path_to_sequence = raw_input('Path to sequence file: ')

sequence_name = path_to_sequence.rpartition('/')[-1]
identifier = str(sequence_name) + '_' + str(randrange(0, 999999999))

def pretty_print_xml(xml):
    rough_string = ET.tostring(xml, 'utf-8')
    reparsed_string = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="  ")

def w_beast_xml(xml_file):
    taxon_name = sequence_name.replace('.nex', '')
    beast_xml = xml_file.readlines()
    for num,item in enumerate(beast_xml):
        item = item.replace('PUT_NAME_OF_FILE_SANS_NEX_HERE', str(taxon_name))
        beast_xml[num] = item
    beast_xml = ''.join(beast_xml)
    beast_xml = ET.XML(beast_xml)
    output.write(ET.tostring(beast_xml, pretty_print=True))

with open('Standard.xml', 'r+') as beast_xml:
    output = open('BEAST_XML_%s.xml' % identifier, 'w')
    w_beast_xml(beast_xml)
    while output.closed != True:
        output.close()