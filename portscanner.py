#!/usr/bin/python

import os
import argparse

from src.colors import Colors
from src.netstructs import *
from src.loadbar import loading_bar

def main():
	parser = argparse.ArgumentParser(description = "Test a specified ip/host for open ports.")
	mutex = parser.add_mutually_exclusive_group(required=True)
	parser.add_argument('hosts', metavar='HOST', help='The ip/host to be scanned for open ports', nargs='*')
	parser.add_argument('-v', '--verbose', help='Add extra verbosity to the output of the scanner', action='store_true')
	parser.add_argument('-t', '--type', help='The type of the ports to be scanned', choices=['tcp', 'TCP', 'udp', 'UDP'], metavar='[ udp | tcp ]', default='tcp')
	mutex.add_argument('-a', '--all', help='Scan all the possible ports', action='store_true')
	mutex.add_argument('-p', '--ports', help='Scan the specified ports only', type=int, metavar='PORT', choices=range(0,65536), nargs='*', default=[])

	args = parser.parse_args()

	ports = []
	if args.all:
		ports = range(0, 65536)
	elif args.ports:
		ports = args.ports
	
	hosts = args.hosts
	for target in hosts:

		host = Host(target)
		ping(host.ip, host.name)	

		open_ports_meta = []
		port_count = 0;
		for port_num in ports:
			port = Port(port_num, args.type.lower())
			if (port.protocol == 'tcp'):								#
				s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)   # Protocol
			elif (port.protocol == 'udp'):                          	# Checking
				s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)    #
			service = Service(port)
			banner = False
			s.settimeout(3)

			port_count += 1
		
			try:
				if args.verbose:
					verbose_message(host.ip, host.name, port.num, port.protocol, service.name)
				s.connect((host.ip, port.num))	# Connect to an ip using the specified port
				s.send("Port Checking")		# Send the message 'Port Checking' to the connected server
				try:
					banner = s.recv(1024)		# Attempt to get a response message
				except socket.timeout:
					banner = ''
			except socket.error:							# If a socket.error exception is caught the attempt to connect has failed, 
				loading_bar(port_count, len(ports), True)
				continue									# hence the port is closed. In that case advance to the next port
			if banner=='':
				banner = 'No Response...'
			open_ports_meta.append((port, service, banner))
			loading_bar(port_count, len(ports), True)
			s.close()

		for item in open_ports_meta:
			results_message(item[0].num, item[0].protocol, item[1].name, item[2])

def verbose_message(ip, hostname, port_num, port_protocol, service_name):   # The extra message printed if the verbose option is on
	print Colors.INFO + '[+] ' + Colors.END + 'Attempting to connect to ' + Colors.INFO + '::' + Colors.END + Colors.HOST + ip + Colors.END + Colors.INFO + ':' + Colors.END + Colors.HOST + hostname + Colors.END + Colors.INFO + '::' + Colors.END + ' via port ' + Colors.PORT + str(port_num) + Colors.END + '/' + Colors.TYPE + port_protocol + Colors.END + ' [' + Colors.SERVICE + service_name.upper() + Colors.END + ']'

def results_message(port_num, port_protocol, serv_name, banner):   # The message printed for open ports
	print Colors.INFO + '[+] ' + Colors.END + 'Port ' + Colors.PORT + str(port_num) + Colors.END + '/' + Colors.TYPE + port_protocol + Colors.END + ' [' + Colors.SERVICE +serv_name.upper() + Colors.END + ']' + ' is open!' + '  ' + Colors.INFO + '==>' + Colors.END + ' Reply: ' + str(banner)

def ping(ip, hostname):   # The ping implementation
	print ''
	print Colors.INFO + '[+] ' + Colors.END + 'Pinging host ' + ip + ":" + hostname
	print ''
	os.system('ping -q -c1 -w2 ' + ip)
	print ''

if __name__ =='__main__':
	main()
