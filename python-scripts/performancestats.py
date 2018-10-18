from __future__ import print_function
import sys
import libvirt
import time
import datetime
import csv

def printascend():
	conn = libvirt.open('qemu:///system')
	if conn == None:
        	print('Failed to open connection to qemu:///system', file=sys.stderr)
        	exit(1)

	domainIDs = conn.listDomainsID()
	if domainIDs == None:
        	print('Failed to get a list of domain IDs', file=sys.stderr)


	dic={}
	if sys.argv[1]=="MEM":
        	for domainID in domainIDs:
                	dom = conn.lookupByID(domainID)
                	if dom == None:
                        	print('Failed to find the domain '+dom.name(), file=sys.stderr)
                        	exit(1)
			
			mem_stats  = dom.memoryStats()
                	dic[domainID]=(1-(float(mem_stats['unused'])/mem_stats['available']))*100
	elif sys.argv[1]=="CPU":
		for domainID in domainIDs:
                	dom = conn.lookupByID(domainID)
                	if dom == None:
                        	print('Failed to find the domain '+dom.name(), file=sys.stderr)
                        	exit(1)

                	cpu_stats1 = dom.getCPUStats(True)
                	cpu_time1=float(cpu_stats1[0]['cpu_time'])/(4*1000000000)
                	dic[domainID]=cpu_time1

        	time.sleep(1)

        	for domainID in domainIDs:
                	dom = conn.lookupByID(domainID)
                	if dom == None:
                        	print('Failed to find the domain '+dom.name(), file=sys.stderr)
                        	exit(1)

                	cpu_stats2 = dom.getCPUStats(True)
                	cpu_time2=float(cpu_stats2[0]['cpu_time'])/(4*1000000000)

               		dic[domainID]=(cpu_time2-dic[domainID])*100
	else:
		print("Please give valid arguement.It either need to be MEM or CPU")
	
	for key, value in sorted(dic.iteritems(), key=lambda (k,v): (v,k)):
        	print("%s	: 	%s" % ((conn.lookupByID(key)).name(), value))

def printthresold():
	alert_file=open('alert_file.csv', mode='w')
	alert_writer = csv.writer(alert_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
	conn = libvirt.open('qemu:///system')
	if conn == None:
        	print('Failed to open connection to qemu:///system', file=sys.stderr)
        	exit(1)

	domainIDs = conn.listDomainsID()
	if domainIDs == None:
        	print('Failed to get a list of domain IDs', file=sys.stderr)

	dic={}
	for domainID in domainIDs:
        	dom = conn.lookupByID(domainID)
        	if dom == None:
                	print('Failed to find the domain '+dom.name(), file=sys.stderr)
                	exit(1)

        	cpu_stats = dom.getCPUStats(True)
        	dic[domainID]=float(cpu_stats[0]['cpu_time'])/(4*1000000000)

	time.sleep(1)
        for domainID in domainIDs:
		dom = conn.lookupByID(domainID)
                if dom == None:
                        print('Failed to find the domain '+dom.name(), file=sys.stderr)
                        exit(1)

                cpu_stats = dom.getCPUStats(True)
                cpu_time=float(cpu_stats[0]['cpu_time'])/(4*1000000000)
                if (cpu_time-dic[domainID])*100 > float(sys.argv[2]):
                	ts = time.time()
                	print('VM name: '+ str(dom.name())+'		time stamp: '+ datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S') + '		CPU usage: '+ str((cpu_time-dic[domainID])*100))
			alert_writer.writerow([str(dom.name()),datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S'),str((cpu_time-dic[domainID])*100)])
	alert_file.close()

def printmavg():
	conn = libvirt.open('qemu:///system')
	if conn == None:
		print('Failed to open connection to qemu:///system', file=sys.stderr)
		exit(1)

	pollsize=int(sys.argv[2])
	windowsize=int(sys.argv[3])

	domainIDs = conn.listDomainsID()
	if domainIDs == None:
        	print('Failed to get a list of domain IDs', file=sys.stderr)

	prevlist={}
	outlist={}
	domsum={}
	for domainID in domainIDs:
        	outlist[domainID]=[]
        	domsum[domainID]=0

	if sys.argv[1]=='CPU':
		for domainID in domainIDs:
        		dom = conn.lookupByID(domainID)
        		if dom == None:
                		prevlist[domainID]=0
        		else:
                		cpu_stats = dom.getCPUStats(True)
                		cpu_time=float(cpu_stats[0]['cpu_time'])/(4*1000000000)
               	 		prevlist[domainID]=cpu_time

		while True:
        		time.sleep(pollsize)
        		dic={}
        		for domainID in domainIDs:
                		dom = conn.lookupByID(domainID)
                		if dom == None:
                        		outlist[domianID].append(0)
                        		prevlist[domainID]=0
                		else:
                        		cpu_stats = dom.getCPUStats(True)
                        		cpu_time=float(cpu_stats[0]['cpu_time'])/(4*1000000000)
                        		cpu_used=cpu_time-prevlist[domainID]
                        		outlist[domainID].append(cpu_used)
                        		domsum[domainID]=domsum[domainID]+cpu_used
                        		prevlist[domainID]=cpu_time

                		if len(outlist[domainID])==windowsize:
                        		dic[domainID]=float(domsum[domainID])/windowsize
                        		domsum[domainID]=domsum[domainID]-outlist[domainID].pop(0)

        		if len(dic)>0:
                		print('-------------------------------------------------------------------------')
                		for key, value in sorted(dic.iteritems(), key=lambda (k,v): (v,k)):
                        		print("%s: %s" % (key, value))
	elif sys.argv[1]=='MEM':
		while True:
			dic={}
			for domainID in domainIDs:
				dom = conn.lookupByID(domainID)
				if dom == None:
                        		outlist[domianID].append(0)
				else:
					mem_stats  = dom.memoryStats()
					outlist[domainID].append(mem_stats['available']-mem_stats['unused'])
					domsum[domainID]=domsum[domainID]+mem_stats['available']-mem_stats['unused']
				
				if len(outlist[domainID])==windowsize:
					dic[domainID]=float(domsum[domainID])/windowsize
					domsum[domainID]=domsum[domainID]-outlist[domainID].pop(0)

			if len(dic)>0:
				print('-------------------------------------------------------------------------')
				for key, value in sorted(dic.iteritems(), key=lambda (k,v): (v,k)):
					print("%s: %s" % (key, value))
			time.sleep(pollsize)
	else:
		print("please give correct parameters")


def main():
	if len(sys.argv)==2:
		printascend()
	elif len(sys.argv)==3:
		printthresold()
	elif  len(sys.argv)==4:
		printmavg()
	else:
		print('please pass required number of parameters as given in readme')




if __name__ == "__main__":
	main()
