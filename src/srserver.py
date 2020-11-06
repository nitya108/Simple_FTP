import sys
import socket
import random
from selectiverepeat import check_checksum, ackss
from util import sr_messages
	
def main():
	window = {}			
	check = True
	seq_number = 0
	port = int(sys.argv[1])		
	file = sys.argv[2]		
	probability_value = float(sys.argv[3])	

	socket_conn  = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)	
	host = socket.gethostname()
	socket_conn.bind((host,port)) 	
		
	while len(window) < seq_number or check:

		msg, addre = socket_conn.recvfrom(1024)
		cs, seq, content, _ = sr_messages(msg) 

		if probability_value <= random.uniform(0,1):
			if check_checksum(int(cs[0]), content) == True:
				if content != '00000end11111':
					if int(seq[0]) not in window:
						window[int(seq[0])] = content	
				elif content == '00000end11111':
					check = False
					seq_number = int(seq[0])				
				packet_ack = ackss(int(seq[0]),0)
				socket_conn.sendto(packet_ack,addre)
		else:
			print('Packet Loss -- SEQ = \t'+str(seq[0]))
	
	packet_ack = ackss(seq_number+1,1)
	socket_conn.sendto(packet_ack,addre)
	f = open(file,'a')
	for i in range(0, seq_number):
		f.write(window[i])
	f.close()
	print('We have recived your file!')
	socket_conn.close()	
	
if __name__ == '__main__':	
	main()