from __future__ import print_function
import sys
import libvirt

conn = libvirt.open('qemu:///system')
if conn == None:
    print('Failed to open connection to qemu:///system', file=sys.stderr)
    exit(1)

#host name
print('Hostname:' +conn.getHostname())

# free memory in host
print('Free memory on the node (host) is ' + str(conn.getFreeMemory()) + ' bytes.')

#maximum number of VCPU's supported per guest by host
print('Maximum support virtual CPUs: '+str(conn.getMaxVcpus(None)))

#type of virtualization in use in the hypervisor
print('Virtualization type: '+conn.getType())

#basically says whether the hypervisor is reachable using TCP connection
print("Connection is alive = " + str(conn.isAlive()))
conn.close()
exit(0)
