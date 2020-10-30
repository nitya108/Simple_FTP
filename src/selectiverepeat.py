import struct
import threading
import time
from util import checksum_calculation

seq_max = -1
lock = threading.Lock()
win = {}
bitflag = True

TIMEOUT_TIMER = 0.2

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
			if constraint > TIMEOUT_TIMER and win[seg][2] == 0:
				print('Timeout, SEQ =\t'+str(seg))
				win[seg] = (win[seg][0], time.time(), 0)
				self.sock.sendto(win[seg][0],(hostname, portnumber))
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
				while len(win) >= self.n:
					self.check_timeout(self.portnumber,self.hostname)
				lock.acquire()
				seg = self.message_from_sender(sendMsg, currSeq)				
				win[currSeq] = (seg, time.time(), 0)
				self.sock.sendto(seg,(self.hostname, self.portnumber))
				lock.release()
				currSeq += 1
				sendMsg = ''
						
		sendMsg = '00000end11111'
		lock.acquire()
		seg = self.message_from_sender(sendMsg, currSeq)				
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
		self.sockAddr = socket
		self.start()
	
	def parseMsg(self, msg):
		zero16 = struct.unpack('=H', msg[4:6])				
		identifier = struct.unpack('=H', msg[6:])			
		seq_number = struct.unpack('=I', msg[0:4])			
		return seq_number, zero16, identifier
		
	def run(self):
		global lock	
		global win
		global bitflag

		bitflag = True
		try:
			while bitflag == True or len(win) > 0:			
				ackReceived, server_addr = self.sockAddr.recvfrom(2048)			 
				seq_number , zero16, identifier = self.parseMsg(ackReceived)
				if int(zero16[0]) > 0:
					print('Receiver Terminated')
					break		
				if int(identifier[0]) == 43690 and int(seq_number[0]) in win:
					lock.acquire()
					setTime = win[int(seq_number[0])][1]
					win[int(seq_number[0])] = (win[int(seq_number[0])][0],setTime, 1)					
					del win[int(seq_number[0])]
					lock.release()
		except:
			print('Server closed its connection - Receiver')
			self.sockAddr.close()
