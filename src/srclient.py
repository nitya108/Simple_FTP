import sys
import socket
import time
from selectiverepeat import client, receiver
from util import client_greeting

def rdtsend():

    hostname = sys.argv[1]
    portnumber = int(sys.argv[2])
    file = sys.argv[3]
    N = int(sys.argv[4])
    MSS = int(sys.argv[5])

    client_greeting(portnumber,file,hostname, MSS, N)

    socket_conn = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)	
    socket_conn.bind(('',4445)) 
	
    time_start = time.time()
    ack = receiver(hostname, portnumber,file,N,MSS,socket_conn)					
    content = client(hostname, portnumber,file,N,MSS,socket_conn, ack) 	

    content.join()
    ack.join()
    time_end = time.time()
    socket_conn.close()

    total_time=time_end-time_start
    print('Delay :\t'+str(total_time))	
	
if __name__ == '__main__':	
	rdtsend()	


