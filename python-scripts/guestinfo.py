from __future__ import print_function
import sys
import libvirt
from xml.dom import minidom


conn = libvirt.open('qemu:///system')
if conn == None:
    print('Failed to open connection to qemu:///system', file=sys.stderr)
    exit(1)

domainIDs = conn.listDomainsID()
if domainIDs == None:
        print('Failed to get a list of domain IDs', file=sys.stderr)

if len(domainIDs)==0:
	print('No active domains to give info',file=sys.stderr)
else:
	dom = conn.lookupByID(domainIDs[0])
	
	#uuid of the domain machine
	print('The UUID of the domain is ' + dom.UUIDString())

	#OS type of domain machine
	print('The OS type of the domain is ' + dom.OSType())

	#name of the domain
	print('The name of the domain is ' + str(dom.name()))

	#max memory of the domain
	print('The max memory for domain is ' + str(dom.maxMemory()) + 'MB')
	
	#max vcpu's of the domain
	print('The max Vcpus for domain is ' + str(dom.maxVcpus()))
conn.close()
exit(0)
