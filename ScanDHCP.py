from PyFunc import *
from xml.dom import minidom

#Global variables are pulled from PyFunc.py

with open('/mnt/sda7/Git/Monitoring/DocScan.xml') as arrDocScan:
	objXMLDocScan = minidom.parse(arrDocScan)
	test = objXMLDocScan.getElementsByTagName('Community')[0].childNodes[0].toxml().strip()
	print test
	
print funcSNMPCommunity()

#objXMLDocScan.close()

#with open('/mnt/sda7/Git/Monitoring/DocScan.xml') as arrDocScan:
#objFile = open('/mnt/sda7/Git/Monitoring/DocScan.xml', 'r')
#arrDocScan = objFile.read()
#objFile.close()
#dom = parseString(arrDocScan)
#xmlTag = dom.getElementsByTagName('Community')[0].toxml()
#print xmlTag


#print doc.toxml()

#print doc.firstChild.childNodes[1].childNodes[0].toxml()
