import struct

null_string = 0

def checksum_calculation(data):
    sum = 0
    modulo2 = len(data) - len(data) % 2
    for i in range(0, modulo2 , 2):
        data = str(data)
        m = (ord(data[i + 1]) << 8)
        w = ord(data[i]) + m
        s1 = ((sum+w) & 0xffff)
        s2 = ((sum + w) >> 16)
        sum =  s1 + s2
    return ~sum & 0xffff

def print_result(hostname,portnumber,N,MSS,end,start):
    timediff = end-start
    print('\t')
    print('Hostname:\t'+str(hostname))
    print('Port Number:\t'+str(portnumber))
    print('MSS:\t'+str(MSS))
    print('Window Size:\t'+ str(N))
    print('Total Time\t'+str(timediff))    

def message_from_sender(data_msg):
    s_num = struct.unpack('=L', data_msg[0:4])
    checksum = struct.unpack('=H', data_msg[4:6])
    pkt = struct.unpack('=h', data_msg[6:8])
    data = (data_msg[8:])
    msg = data.decode('ISO-8859-1','ignore')
    return s_num, checksum, pkt, msg

def greeting(port,fname,prob,host):
    print("Server Portnumber \t: " + str(port))
    print("File being written \t: " + fname)
    print("P value \t\t: " + str(prob))
    print("Host \t\t\t: "+ host)
    print("\n")

def wite_to_file(file_name, data, expected_sequence, data_packet_acknowledgment, soc_receiver, checksum, address):
    with open(file_name, 'ab') as file:
        print("Message size recived: " + str(checksum[0]))
        file.write(str.encode(data))
        seq_number = struct.pack('=I', expected_sequence)
        null = struct.pack('=H', null_string)
        
        acknowledgment_sent = struct.pack('=H',data_packet_acknowledgment)
        acknowledgment = seq_number + null + acknowledgment_sent
        soc_receiver.sendto(acknowledgment, address)