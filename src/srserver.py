import sys
import socket
import struct
import random
from selectiverepeat import check_checksum, ackss

def unpack_message(msg):					#Parsing the Message received from client
	header = msg[0:8]
	content = msg[8:]	
	seq = struct.unpack('=I',header[0:4])		
	cs = struct.unpack('=H',header[4:6])
	identifier = struct.unpack('=H',header[6:])
	dataDecoded = content.decode('UTF-8')	
	return seq, cs, identifier, dataDecoded
	
def main():
	port = int(sys.argv[1])		
	file = sys.argv[2]		
	probability_value = float(sys.argv[3])	
	window = {}			
	check = True
	seq_number = 0
	
	socket_conn  = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)	
	host = socket.gethostname()
	socket_conn.bind((host,port)) 
	
		
	while check or len(window) < seq_number:
		msg, addre = socket_conn.recvfrom(1024)
		seq, cs, _ , content = unpack_message(msg) 
		if random.uniform(0,1) <= probability_value:
			print('PACKET LOSS, SEQUENCE NUMBER = '+str(seq[0]))
		else:
			if check_checksum(content, int(cs[0])) == True:
				if content == '00000end11111':
					check = False
					seq_number = int(seq[0])
				elif content != '00000end11111' and int(seq[0]) not in window:
						window[int(seq[0])] = content						
				packet_ack = ackss(int(seq[0]),0)
				socket_conn.sendto(packet_ack,addre)
	
	packet_ack = ackss(seq_number+1,1)
	socket_conn.sendto(packet_ack,addre)
	f = open(file,'a')
	for i in range(0, seq_number):
		f.write(window[i])
	f.close()
	print('File Received Successfully at the Server')
	socket_conn.close()	
	
if __name__ == '__main__':	
	main()