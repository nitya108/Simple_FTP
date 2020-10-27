import socket
import sys
import struct
import random

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

def message_from_sender(data_msg):
    s_num = struct.unpack('=L', data_msg[0:4])
    checksum = struct.unpack('=H', data_msg[4:6])
    pkt = struct.unpack('=h', data_msg[6:8])
    data = (data_msg[8:])
    msg = data.decode('ISO-8859-1','ignore')
    return s_num, checksum, pkt, msg

def server_receiver():
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
                if checksum[0] == checksum_computation(data):
                    wite_to_file(fname, data, seq, pkt_ack, receiver, checksum, addr)
                    seq += 1

def carry_around_add(x, y):
    return ((x + y) & 0xffff) + ((x + y) >> 16)

def checksum_computation(data_msg):
    add = 0
    for i in range(0, len(data_msg) - len(data_msg) % 2, 2):
        data_msg = str(data_msg)
        w = ord(data_msg[i]) + (ord(data_msg[i + 1]) << 8)
        add = carry_around_add(add, w)
    return ~add & 0xffff

if __name__ == '__main__':
    server_receiver()