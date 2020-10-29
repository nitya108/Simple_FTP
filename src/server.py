import socket
import sys
import struct
import random
from util import checksum_calculation, message_from_sender, wite_to_file, greeting

pkt_ack = 46710

def main():
    port = int(sys.argv[1])
    fname = sys.argv[2]
    prob = float(sys.argv[3])

    seq = 1
    receiver = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    host = socket.gethostname()
    greeting(port,fname,prob,host)
    receiver.bind((host, port))

    while True:
        data_msg, addr = receiver.recvfrom(2048)
        num_sequence, checksum, _ , data = message_from_sender(data_msg)
        print('SEQ: ' +str(num_sequence[0]))

        if( random.random() > prob ):
            if seq == num_sequence[0]:
                if checksum[0] == checksum_calculation(data):
                    wite_to_file(fname, data, seq, pkt_ack, receiver, checksum, addr)
                    seq += 1
        else:
            seqno=str(num_sequence[0])
            print('PACKET LOSS, SEQ = '+ seqno)

if __name__ == '__main__':
    main()