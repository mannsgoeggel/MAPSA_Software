#Functions related to data aquisition at the MPA level

from MAPSA_functions import *
class MPA_daq:
	
	def __init__(self, hw, nmpa):
		self._hw     = hw
		self._nmpa     = nmpa

		self._Shutter   	= 	self._hw.getNode("Shutter")
		self._Control		=	self._hw.getNode("Control")
		self._Configuration 	=  	self._hw.getNode("Configuration")
		self._Readout 		=  	self._hw.getNode("Readout")


		self._puls_num   = self._Shutter.getNode("Strobe").getNode("number")
		self._puls_len   = self._Shutter.getNode("Strobe").getNode("length")
		self._puls_dist  = self._Shutter.getNode("Strobe").getNode("distance")
		self._puls_del   = self._Shutter.getNode("Strobe").getNode("delay")
		self._shuttertime	= self._Shutter.getNode("time")

		self._busy  = self._Control.getNode("Sequencer").getNode("busy")
		self._calib  = self._Control.getNode("Sequencer").getNode("calibration")
		self._read  = self._Control.getNode("Sequencer").getNode("readout")
		self._buffers  = self._Control.getNode("Sequencer").getNode("buffers_index")
		self._data_continuous  = self._Control.getNode("Sequencer").getNode("datataking_continuous")



		self._memory  = self._Readout.getNode("Memory")
		self._counter  = self._Readout.getNode("Counter")
		self._busyread  = self._Readout.getNode("busy")

		self._readmode  = self._Readout.getNode("memory_readout")
		self._readbuff  = self._Readout.getNode("buffer_num")


	def _waitreadout(self):
		busyread = self._busyread.read()
		self._hw.dispatch()
		count = 0
		while busyread:
			time.sleep(0.005)
			busy = self._busyread.read()
		        self._hw.dispatch()
			count = count + 1
			if count > 100:
				print "readout Idle"
				return 0
		#print "Finished"
		#print "Readout took " + str(count*0.005) + " seconds"
                return 1
				


	def read_raw(self,buffer_num,dcindex):
		print "dcindex " +str(dcindex)
		counter_data  = self._counter.getNode("MPA"+str(dcindex)).readBlock(25)
		counter_data1  = self._counter.getNode("MPA1").readBlock(25)
		counter_data2  = self._counter.getNode("MPA2").readBlock(25)
		counter_data3  = self._counter.getNode("MPA3").readBlock(25)
		counter_data4  = self._counter.getNode("MPA4").readBlock(25)
		counter_data5  = self._counter.getNode("MPA5").readBlock(25)
		counter_data6  = self._counter.getNode("MPA6").readBlock(25)
		memory_data = self._memory.getNode("MPA"+str(self._nmpa)).getNode("buffer_"+str(buffer_num)).readBlock(216)

		self._hw.dispatch()
		self._waitreadout()
		print "MPA1 "
		print counter_data1
		print 
		print "MPA2 "
		print counter_data2
		print 
		print "MPA3 "
		print counter_data3
		print 
		print "MPA4 "
		print counter_data4
		print 
		print "MPA5 "
		print counter_data5
		print 
		print "MPA6 "
		print counter_data6

		return [memory_data,counter_data]

	def read_data(self,buffer_num,dcindex=-1):
		if dcindex==-1:
			dcindex=self._nmpa
		(memory_data,counter_data)= self.read_raw(buffer_num,dcindex)

		#print memory_data
		#print counter_data
		pix = [None]*50
		mem = [None]*96
		for x in range(0,25):

			pix[2*x]  = int((counter_data[x] >> 3) & 0xffff)
			pix[2*x+1]= int((counter_data[x] >> 19) & 0xffff)

		memory_string = '';
		for x in range(0,216):
			memory_string = memory_string + str(hex_to_binary(frmt(memory_data[215 - x])))
		for x in range(0,96):
			mem[x] = memory_string [x*72 : x*72+72]			

		return pix,mem	


##############UNEDITED			


	def read_memory(self, mem,mode):

		memory = np.array(mem)
		BX = []
		hit = []
		row = []
		col = []
		data = []
		bend = []
		
		if (mode == 2):
			for x in range(0,96):
				if (memory[x][0:16] == '00000000'):
					break
				BX.append(int(memory[x][0:16],2))
				nrow = [int(memory[x][16:21],2), int(memory[x][23:28],2), int(memory[x][30:35],2), int(memory[x][37:42],2), int(memory[x][44:49],2), int(memory[x][51:56],2), int(memory[x][58:63],2), int(memory[x][65:70],2)]
				#nrow = filter(lambda a: a !=0, nrow)
				ncol = [int(memory[x][21:23],2), int(memory[x][28:30],2), int(memory[x][35:37],2), int(memory[x][42:44],2), int(memory[x][49:51],2), int(memory[x][56:58],2), int(memory[x][63:65],2), int(memory[x][70:72],2)] 
				ncol = filter(lambda a: a !=0, ncol)
				if (ncol != []):
					nrow = nrow[8-len(ncol):8]
					col.append(ncol)
					row.append(nrow)
			data = [row,col]
		
		if (mode == 0):
			for x in range(0,96):
				if (memory[x][0:16] == '00000000'):
					break
				BX.append(int(memory[x][4:20],2))
				nrow = [int(memory[x][20:26],2), int(memory[x][33:39],2), int(memory[x][46:52],2), int(memory[x][59:65],2)]
				nbend = [int(memory[x][26:31],2), int(memory[x][39:44],2), int(memory[x][52:57],2), int(memory[x][65:70],2)] 
				ncol = [int(memory[x][31:33],2), int(memory[x][44:46],2), int(memory[x][57:59],2), int(memory[x][70:72],2)] 
				ncol = filter(lambda a: a !=0, ncol)
				
				
				if (ncol != []):
					nrow = nrow[4-len(ncol):4]
					nbend = nbend[4-len(ncol):4]
					col.append(ncol)
					row.append(nrow)
					bend.append(nbend)
			data = [row, bend, col]
		
		if (mode == 3):
			for x in range(0,96):
				if (memory[x][0:8] == '00000000'):
					break
				BX.append(int(memory[x][8:24],2))
				hit.append(memory [x][24:72])			
			
			hit = filter(lambda a: a!=0, hit)
			data = hit		
		
		BX = filter(lambda a: a!=0, BX)		
		return BX, data	
			
	
	


	
			
			
