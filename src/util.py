import struct

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
    print('MSS:\t\t'+str(MSS))
    print('Window Size:\t'+ str(N))
    print('Total Time\t'+str(timediff))    

def decode_msg(ack):
    running_seq = struct.unpack('=I', ack[0:4])
    running_seq = int(running_seq[0])
    check_ack = struct.unpack('=H', ack[6:8])
    return running_seq,check_ack

def sender(data_msg):
    s_num = struct.unpack('=L', data_msg[0:4])
    checksum = struct.unpack('=H', data_msg[4:6])
    pkt = struct.unpack('=h', data_msg[6:8])
    data = (data_msg[8:])
    msg = data.decode('ISO-8859-1','ignore')
    return s_num, pkt, msg, checksum

def server_greeting(port,fname,prob,host):
    print("------------------------------------ SERVER SIDE ------------------------------------------")
    print("Server Portnumber \t: " + str(port))
    print("File being written \t: " + fname)
    print("P value \t\t: " + str(prob))
    print("Host \t\t\t: "+ host)
    print("\n")

def client_greeting(port,file,host, MSS, N):
    print("------------------------------------ CLIENT SIDE ------------------------------------------")
    print("Hostname \t: " + str(host))
    print("Port Number \t: " + str(port))
    print("Filename \t: " + str(file))
    print("N \t\t: "+ str(N))
    print("MSS \t\t: "+ str(MSS))
    print("\n")

def wite_to_file( seq, file, second,socket, checksum, ack, addr):

    with open(file, 'ab') as file:
        print("Message size recived: " + str(checksum[0]))
        file.write(str.encode(second))
        seq_number = struct.pack('=I', seq)
        null = struct.pack('=H', 0)
        
        sent_ack = struct.pack('=H',ack)
        final_ack = seq_number + null + sent_ack
        socket.sendto(final_ack, addr)

def message(data):
		bitbuffer = struct.unpack('=H', data[4:6])				
		check = struct.unpack('=H', data[6:])			
		seq_number = struct.unpack('=I', data[0:4])			
		return seq_number, bitbuffer, check

def sr_messages(msg):				
    first = msg[0:8]
    seq = struct.unpack('=I',first[0:4])
    cs = struct.unpack('=H',first[4:6])
    id = struct.unpack('=H',first[6:])
    second = msg[8:]
    content = second.decode('UTF-8')
    return cs, seq, content, id