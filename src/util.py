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