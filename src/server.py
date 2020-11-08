import socket
import sys
import struct
import random
from util import checksum_calculation, sender, wite_to_file, server_greeting

pkt_ack = 46710

def receive(port,fname,prob):
    seq = 1
    receiver = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    host = socket.gethostname()
    server_greeting(port,fname,prob,host)
    receiver.bind((host, port))
    flag =0

    while True:
        data_msg, addr = receiver.recvfrom(2048)
        num_sequence, _ , data, checksum = sender(data_msg)
        print('SEQ: ' +str(num_sequence[0]))
        if flag == 0:
            print("ACK received")
            flag +=1
        if( random.random() > prob ):
            if seq == num_sequence[0]:
                if checksum[0] == checksum_calculation(data):
                    wite_to_file(seq, fname, data, receiver, checksum, pkt_ack,addr)
                    seq += 1
        else:
            seqno = str(num_sequence[0])
            print('PACKET LOSS, SEQ = '+ seqno)
    

if __name__ == '__main__':
    port = int(sys.argv[1])
    fname = sys.argv[2]
    prob = float(sys.argv[3])
    receive(port,fname,prob)