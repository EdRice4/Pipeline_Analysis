from random import randrange

identifier = randrange(0, 999999999)

def w_beast_xml(xml_file):
    beast_xml = xml_file.readlines()
    for num,value in enumerate(beast_xml):
    	return num, value

with open('Standard.xml', 'r+') as beast_xml:
    output = open('BEAST_XML_%s.xml' % identifier, 'w')
    print w_beast_xml(beast_xml)
    while output.closed != True:
        output.close()