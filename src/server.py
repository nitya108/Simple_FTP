import socket
import sys
import struct
import random
from util import checksum_calculation, message_from_sender

pkt_ack = 43690
null_string = 0

def wite_to_file(file_name, data, expected_sequence, data_packet_acknowledgment, soc_receiver, checksum, address):
    with open(file_name, 'ab') as file:
        print("FILE received and size of chunk: " + str(checksum))
        file.write(str.encode(data))
        seq_number = struct.pack('=I', expected_sequence)
        null = struct.pack('=H', null_string)
        acknowledgment_sent = struct.pack('=H',data_packet_acknowledgment)
        acknowledgment = seq_number + null + acknowledgment_sent
        soc_receiver.sendto(acknowledgment, address)

def main():
    port = int(sys.argv[1])
    fname = sys.argv[2]
    prob = float(sys.argv[3])

    print("Server's port - " + str(port))
    print("filename - " + fname)
    print("probability - " + str(prob))

    seq = 1
    receiver = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    host = socket.gethostname()
    print("hostname: "+ host)
    receiver.bind((host, port))

    while True:
        data_msg, addr = receiver.recvfrom(2048)
        print("address "+ str(addr))
        num_sequence, checksum, _ , data = message_from_sender(data_msg)
        print('sequence number' +str(num_sequence))

        if(random.random()<prob):
            print('PACKET LOSS,SEQUENCE NUMBER = '+ str(num_sequence[0]))
        else:
            if seq == num_sequence[0]:
                if checksum[0] == checksum_calculation(data):
                    wite_to_file(fname, data, seq, pkt_ack, receiver, checksum, addr)
                    seq += 1

if __name__ == '__main__':
    main()