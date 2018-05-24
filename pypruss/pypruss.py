import os
import sys
import subprocess
import io
import select
import mmap
import struct

#State definitions
PRU_OFFLINE = 0
PRU_STOPPED = 1
PRU_RUNNING = 2
PRU_HALTED  = 3

#Memory definitions
PRU_ICSS     = 0x4A300000
PRU_ICSS_LEN = 512*1024
PRU_DRAM0    = 0x00000000
PRU_DRAM1    = 0x00002000
PRU_SRAM     = 0x00010000

class PRU(object):

    def __init__(self, number=0, fw=None):
        if number != 0 and number != 1:
            sys.exit("Invalid PRU number (Can be 0 or 1 only)")
        self.number = number
        self.modprobe()
        self.reset()
        if fw is not None:
            self.load(fw)
		
    @classmethod 
    def modprobe(cls):
        if subprocess.call("/sbin/modprobe pru_rproc", shell=True) :
    	    sys.exit("Probing Remoteproc Driver Failed")
    
    @classmethod
    def modunprobe(cls):
        if subprocess.call("/sbin/modprobe -r pru_rproc", shell=True) :
            sys.exit("Failed removing the Remoteproc Driver")

    def enable(self):
        try:
            with open('/sys/class/remoteproc/remoteproc'+str(self.number+1)+'/state', 'w') as fd:
                fd.write('start')
                fd.close()
            self.state = PRU_RUNNING
        except OSError:
            pass 

    def disable(self):
        try:
            with open('/sys/class/remoteproc/remoteproc'+str(self.number+1)+'/state', 'w') as fd:
                fd.write('stop')
                fd.close();
            self.state = PRU_STOPPED
        except OSError:
            pass
	
    def reset(self):
        self.disable()
        self.enable()
    	
    def load(self, filepath):
        self.disable()
        if subprocess.call('cp '+filepath+' /lib/firmware/am335x-pru'+str(self.number)+'-fw', shell=True):
            print("Error loading firmware on PRU"+str(self.number))
        self.enable()

        # RPMsg functions
    def send_msg(self, message, channel=None):
        if channel is None:
            channel = '3'+str(self.number)
        devpath = '/dev/rpmsg_pru'+str(channel)
        if os.path.exists(devpath):
            with open(devpath, 'w') as fd:
                fd.write(message+'\n');
                fd.close()
        else:
            print("Error Sending Message on "+channel+": Channel not found")

    def get_msg(self, channel=None):
        if channel is None:
            channel = '3'+str(self.number)
        devpath = '/dev/rpmsg_pru'+str(channel)
        if os.path.exists(devpath):
            with io.open(devpath, 'r') as fd:
                data = fd.readline().strip()
                fd.close()
            return data
        else:
            print("Error Recieving Message from "+channel+": Channel not found")

    def wait_for_event(self, channel=None):
        if channel is None:
            channel = '3'+str(self.number)
        devpath = '/dev/rpmsg_pru'+str(channel)
        if os.path.exists(devpath):
            with open(devpath, 'r') as fd:
                fd.read(1);
                fd.close()
        else:
            print("Error : Channel not found")
            
	#Memory functions
    def mem_writeint(self, address, data, shared=False):
        base = PRU_SRAM if shared else (PRU_DRAM1 if self.number else PRU_DRAM0)
        with open('/dev/mem', 'r+b') as fd:
            pru_mem = mmap.mmap(fd.fileno(), PRU_ICSS_LEN, offset=PRU_ICSS)
            pru_mem[base+address: base+address+4] = struct.pack('L', data)
            pru_mem.close()
            fd.close()
	
    def mem_readint(self, address, shared=False):
        base = PRU_SRAM if shared else (PRU_DRAM1 if self.number else PRU_DRAM0)
        with open('/dev/mem', 'r+b') as fd:
            pru_mem = mmap.mmap(fd.fileno(), PRU_ICSS_LEN, offset=PRU_ICSS)
            data = struct.unpack('L', pru_mem[base+address: base+address+4])[0]
            pru_mem.close()
            fd.close()
        return data
    	
    def mem_writebyte(self, address, data, shared=False):
        base = PRU_SRAM if shared else (PRU_DRAM1 if self.number else PRU_DRAM0)
        with open('/dev/mem', 'r+b') as fd:
            pru_mem = mmap.mmap(fd.fileno(), PRU_ICSS_LEN, offset=PRU_ICSS)
            pru_mem[base+address: base+address+1] = struct.pack('B', data)
            pru_mem.close()
            fd.close()
	
    def mem_readbyte(self, address, shared=False):
        base = PRU_SRAM if shared else (PRU_DRAM1 if self.number else PRU_DRAM0)
        with open('/dev/mem', 'r+b') as fd:
            pru_mem = mmap.mmap(fd.fileno(), PRU_ICSS_LEN, offset=PRU_ICSS)
            data = struct.unpack('B', pru_mem[base+address: base+address+1])[0]
            pru_mem.close()
            fd.close()
        return data
