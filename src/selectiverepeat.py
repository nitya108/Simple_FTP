import struct
import threading
import time
from util import checksum_calculation

seq_max = -1
lock = threading.Lock()
win = {}
bitflag = True

TIMEOUT_TIMER = 0.2

def check_checksum(content, cs):
	sum = 0
	
	for i in range(0, len(content), 2):
		if i+1 < len(content):
			data16 = ord(content[i]) + (ord(content[i+1]) << 8)		
			interSum = sum + data16
			sum = (interSum & 0xffff) + (interSum >> 16)		
	currChk = sum & 0xffff 
	result = currChk & cs
	
	if result != 0:
		return False
	else:
		return True

def ackss(seqAcked, type):
	seqNum 		 = struct.pack('=I', seqAcked)		
	if type != 0:
		zero16 	 = struct.pack('=H', 1)
	else:
		zero16 	 = struct.pack('=H', 0)
	ackIndicator = struct.pack('=H',43690)		
	packet_ack = seqNum+zero16+ackIndicator
	return packet_ack

class client(threading.Thread):
	def __init__(self, hostname, portnumber, file, n, MSS, socket, receiver):
		threading.Thread.__init__(self)					
		self.portnumber = int(portnumber)
		self.n    = int(n)				
		self.MSS  = int(MSS)			
		self.file = file				
		self.hostname = hostname				
		self.sock = socket
		self.r = receiver
		self.start()		
				
	def run(self):
		self.rdt_send()

	def check_timeout(self, portnumber, hostname):
		global lock
		global win
		global seq_max
		
		lock.acquire()
		for seg in win:
			constraint = time.time() - win[seg][1]
			if constraint > TIMEOUT_TIMER:
				if win[seg][2] == 0 :
					print('Timeout, SEQ =\t'+str(seg))
					m =win[seg][0]
					win[seg] = ( m, time.time(), 0)
					self.sock.sendto(m,(hostname, portnumber))
		lock.release()

	def message_from_sender(self, content, num_seq):
		c = checksum_calculation(content)
		checksum = struct.pack('=H', c)
		s_num = struct.pack('=I',num_seq)
		pkt = struct.pack('=H',21845)
		seg = s_num + checksum + pkt + bytes(content,'UTF-8')
		return seg
		
	def rdt_send(self):
		global lock
		global win
		global seq_max
		currSeq = 0
		sendMsg = ''
		b = True

		f = open(self.file,'rb')
		while b:
			b = f.read(1)
			sendMsg += str(b,'UTF-8')
			if len(sendMsg) == self.MSS or (not b):		
				while self.n <= len(win):
					self.check_timeout(self.portnumber,self.hostname)
				lock.acquire()

				seg = self.message_from_sender(sendMsg, currSeq)				
				win[currSeq] = (seg, time.time(), 0)
				self.sock.sendto(seg,(self.hostname, self.portnumber))
				lock.release()
				currSeq += 1
				sendMsg = ''
						 
		lock.acquire()
		seg = self.message_from_sender('00000end11111', currSeq)				
		win[currSeq] = (seg, time.time(), 0)
		self.sock.sendto(seg,(self.hostname, self.portnumber))
		lock.release()

		seq_max = currSeq
		while len(win) > 0:
			self.check_timeout(self.portnumber,self.hostname)
		f.close()	
		
class receiver(threading.Thread):
	def __init__(self, hostname, portnumber, file, n, MSS, socket):		
		threading.Thread.__init__(self)
		self.hostname = hostname				
		self.portnumber = int(portnumber)			
		self.file = file				
		self.n    = int(n)				
		self.MSS  = int(MSS)			
		self.sockconn = socket
		self.start()
	
	def parseMsg(self, msg):
		buff = struct.unpack('=H', msg[4:6])				
		number = struct.unpack('=H', msg[6:])			
		sequ = struct.unpack('=I', msg[0:4])			
		return sequ, buff, number
		
	def run(self):
		global lock	
		global win
		global bitflag

		bitflag = True
		try:
			while bitflag == True or len(win) > 0:			
				ackReceived, _ = self.sockconn.recvfrom(2048)			 
				sequ , buff, number = self.parseMsg(ackReceived)
				if int(buff[0]) > 0:
					print('Receiver Terminated')
					break		
				if int(number[0]) == 43690:
					if int(sequ[0]) in win:
						lock.acquire()
						win[int(sequ[0])] = (win[int(sequ[0])][0],win[int(sequ[0])][1], 1)					
						del win[int(sequ[0])]
						lock.release()
		except:
			print('Server closed its connection - Receiver')
			self.sockconn.close()
