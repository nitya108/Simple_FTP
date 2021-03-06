import threading
import sys
import time
import struct
import socket
from util import checksum_calculation,print_result, decode_msg, client_greeting

data_buffer         = []
buffer_for_sending  = {'a':'a'}
current_ack         = 0
ack_of_packet       = 0
total_no_packets    = 1

PACKET_ID   = 23633
TIMER       = 3

lock = threading.Lock()

class ackclass(threading.Thread):
    
    def __init__(self, client):
        threading.Thread.__init__(self)
        self.client = client
        self.flag =1
        self.start()

    def run(self):
        global current_ack
        global ack_of_packet
        try:
            while ack_of_packet < total_no_packets:
                ack, _ = self.client.recvfrom(2048)
                ack_of_packet  = ack_of_packet + 1
                current_ack = current_ack + 1
                if self.flag == 0:
                    print("ACK received")
                    self.flag +=1
                running_seq,  check_ack = decode_msg(ack)

                if check_ack[0] == PACKET_ID:
                    lock.acquire()
                    del buffer_for_sending[running_seq-1]
                    lock.release()

        except ConnectionResetError:
            print("Error")
            self.client.close()

class serverclass(threading.Thread):
    def __init__(self, portnumber, hostname, client, file, MSS, N):
        threading.Thread.__init__(self)
        self.portnumber = portnumber
        self.hostname = hostname
        self.client = client
        self.file = file
        self.MSS  = MSS
        self.N    = N
        self.flag = 1
        self.start()

    def run(self):

        n = 0
        server =  (self.hostname, self.portnumber)

        while total_no_packets > ack_of_packet :
            while n - current_ack >= self.N:
                if self.flag == 0:
                    print("getting ack")
                    self.flag +=1
                lock.acquire()
                if current_ack < n and current_ack < total_no_packets:
                    self.func_timeout(n, server)
                lock.release()

            lock.acquire()
            if current_ack < n and total_no_packets <= self.N:
                self.func_timeout(n, server)
            lock.release()

            lock.acquire()
            if current_ack < n and current_ack < total_no_packets:
                self.func_timeout(n, server)
            lock.release()

            lock.acquire()
            if n < total_no_packets:
                buffer_for_sending[n] = (data_buffer[n],time.time())
                self.client.sendto(data_buffer[n], server)
                n = n + 1
            lock.release()

    def func_timeout(self, n, server):
        if buffer_for_sending.get(current_ack):
            try:
                if self.flag == 0:
                    print("buffer")
                    self.flag +=1
                packet_time = (time.time()-((buffer_for_sending[current_ack])[1]))
                if packet_time >= TIMER:
                    for cur_pkt in range(current_ack, n):
                        if self.flag == 0:
                            print("received")
                            self.flag +=1
                        file_data = buffer_for_sending [cur_pkt][0]
                        buffer_for_sending[cur_pkt] = (file_data, time.time())
                        self.client.sendto(file_data,server)
                        print('TIMEOUT!! SEQ NO = '+str(cur_pkt))
            except KeyError:
                print("...")


def rdt_send():

    hostname = sys.argv[1]
    portnumber = int(sys.argv[2])
    file = sys.argv[3]
    N = int(sys.argv[4])
    MSS = int(sys.argv[5])

    client_greeting(portnumber,file,hostname, MSS, N)

    global data_buffer
    global total_no_packets

    start = time.time()
    
    IPclient = ''
    client_port_no = 4445
    client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client.bind((IPclient,client_port_no))
    

    FILE = open(file,'rb')
    file_data = FILE.read(MSS)
    seq = 1
    while file_data:
        file_content = str(file_data,'UTF-8',errors='replace')
        cs = checksum_calculation(file_content)
        checksum = struct.pack('=H', cs)
        seq_no = struct.pack('=L',seq)
        data = file_content.encode('ISO-8859-1','ignore')
        initial_packet = struct.pack('=h',PACKET_ID)
        cur_pkt = seq_no + checksum + initial_packet + data
        data_buffer.append(cur_pkt)
        file_data = FILE.read(MSS)
        seq += 1
    total_no_packets = len(data_buffer)

    ACKs = ackclass(client)
    transmitted_data = serverclass(portnumber, hostname, client, file, MSS, N)
    transmitted_data.join()
    ACKs.join()
    end = time.time()
    client.close()
    print_result(hostname,portnumber,N,MSS,end,start)
    FILE.close() 


if __name__ == '__main__':
    rdt_send()