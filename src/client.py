import time
import signal
import socket
import inspect
import struct
import sys
import threading

TIMEOUT_TIMER = 3
DATA_PACKET_IDENTIFIER = 21845
current_ack = 0
seq_latest = 0
data_buffer = []
buffer_for_sending = {'a':'a'}
packets_sent = 0
total_no_packets = 1
ack_of_packet = 0
lock = threading.Lock()


def perform_timeout_operation(n, self, server):
    if buffer_for_sending.get(current_ack):
        try:
            if (time.time()-((buffer_for_sending[current_ack])[1])) >= TIMEOUT_TIMER:
                for cur_pkt in range(current_ack, n):
                    file_data = buffer_for_sending [cur_pkt][0]
                    buffer_for_sending[cur_pkt] = (file_data, time.time())
                    self.client.sendto(file_data,server)
                    print('Timeout, Sequence Number = '+str(cur_pkt))
        except KeyError:
            print(" ")

class Sender(threading.Thread):
    def __init__(self, hostname, portnumber, file, N, MSS, client):
        threading.Thread.__init__(self)
        self.hostname = hostname
        self.portnumber = portnumber
        self.file = file
        self.N    = N
        self.MSS  = MSS
        self.client = client
        self.start()

    def run(self):
        global buffer_for_sending
        global lock
        global current_ack
        global seq_latest
        global total_no_packets
        global data_buffer
        global ack_of_packet

        n = 0
        server = (self.hostname, self. portnumber)

        while ack_of_packet < total_no_packets:
            #go-back-n main logic
            while n - current_ack >= self.N:
                lock.acquire()
                if current_ack < total_no_packets and current_ack < n:
                    perform_timeout_operation(n, self, server)
                    # if buffer_for_sending.get(current_ack):
                    #     try:
                    #         if (time.time()-((buffer_for_sending[current_ack])[1])) >= TIMEOUT_TIMER:
                    #             for cur_pkt in range(current_ack, n):
                    #                 file_data = buffer_for_sending [cur_pkt][0]
                    #                 buffer_for_sending[cur_pkt] = (file_data, time.time())
                    #                 self.client.sendto(file_data,server)
                    #                 print('Timeout, Sequence Number = '+str(cur_pkt))
                    #     except KeyError:
                    #         print(" ")
                lock.release()

            lock.acquire()
            if total_no_packets <= self.N and current_ack < n:
                perform_timeout_operation(n, self, server)
                # if buffer_for_sending.get(current_ack):
                #     try:
                #         if (time.time()-((buffer_for_sending[current_ack])[1])) >= TIMEOUT_TIMER:
                #             for cur_pkt in range(current_ack, n):
                #                 file_data = buffer_for_sending [cur_pkt][0]
                #                 buffer_for_sending[cur_pkt] = (file_data, time.time())
                #                 self.client.sendto(file_data,server)
                #                 print('Timeout, Sequence Number = '+str(cur_pkt))
                #     except KeyError:
                #         print(" ")
            lock.release()


            lock.acquire()
            if current_ack < total_no_packets and current_ack < n:
                perform_timeout_operation(n, self, server)
                # if buffer_for_sending.get(current_ack):
                #     try:
                #         if (time.time()-((buffer_for_sending[current_ack])[1])) >= TIMEOUT_TIMER:
                #             for cur_pkt in range(current_ack, n):
                #                 file_data = buffer_for_sending [cur_pkt][0]
                #                 buffer_for_sending[cur_pkt] = (file_data, time.time())
                #                 self.client.sendto(file_data,server)
                #                 print('Timeout, Sequence Number = '+str(cur_pkt))
                #     except KeyError:
                #         print(" ")
            lock.release()

            lock.acquire()
            if n < total_no_packets:
                buffer_for_sending[n] = (data_buffer[n],time.time())
                self.client.sendto(data_buffer[n], server)
                n = n + 1
            lock.release()

class Acknowledgment(threading.Thread):
    def __init__(self, client):
        threading.Thread.__init__(self)
        self.client = client
        self.start()

    def run(self):
        global buffer_for_sending
        global lock
        global current_ack
        global seq_latest
        global total_no_packets
        global data_buffer
        global ack_of_packet

        try:
            while ack_of_packet < total_no_packets:
                ack, address = self.client.recvfrom(2048)
                ack_of_packet  = ack_of_packet + 1
                current_ack = current_ack + 1
                running_seq = struct.unpack('=I', ack[0:4])
                running_seq = int(running_seq[0])
                check_ack = struct.unpack('=H', ack[6:8])
                if check_ack[0] == DATA_PACKET_IDENTIFIER:
                    lock.acquire()
                    del buffer_for_sending[running_seq-1]
                    lock.release()

        except ConnectionResetError:
            print("Error")
            self.client.close()

def compute_carry(a, b):
    return ((a+b) & 0xffff) + ((a + b) >> 16)

def checksum_computation(data):
    sum = 0
    for i in range(0, len(data) - len(data) % 2, 2):
        data = str(data)
        w = ord(data[i]) + (ord(data[i + 1]) << 8)
        sum = compute_carry(sum, w)
    return ~sum & 0xffff

def main():
    hostname = sys.argv[1]
    portnumber = int(sys.argv[2])
    file = sys.argv[3]
    N = int(sys.argv[4])
    MSS = int(sys.argv[5])
    start = time.time()
    global data_buffer
    global total_no_packets
    IPclient = ''
    client_port_no = 4445
    client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client.bind((IPclient,client_port_no))
    FILE = open(file,'rb')
    file_data = FILE.read(MSS)
    seq = 1
    while file_data:
        file_content = str(file_data)
        checksum = checksum_computation(file_content)
        checksum = struct.pack('=H', checksum)
        seq_no = struct.pack('=L',seq)
        data = file_content.encode('ISO-8859-1','ignore')
        initial_packet = struct.pack('=h',DATA_PACKET_IDENTIFIER)
        cur_pkt = seq_no + checksum + initial_packet + data
        data_buffer.append(cur_pkt)
        file_data = FILE.read(MSS)
        seq += 1
    total_no_packets = len(data_buffer)
    ACKs = Acknowledgment(client)
    transmitted_data = Sender(hostname, portnumber, file, N, MSS, client)
    transmitted_data.join()
    ACKs.join()
    end = time.time()
    client.close()
    print('hostname:\t'+str(hostname))
    print('portnumber:\t'+str(portnumber))
    print('Window Size:\t'+ str(N))
    print('Maximum Segment Size:\t'+str(MSS))
    print('End Time\t'+str(end))
    print('Total Time\t'+str(end-start))
    FILE.close() 

if __name__ == '__main__':
    main()