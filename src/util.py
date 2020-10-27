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