import os
import subprocess
import io
import select
import mmap
import struct

#Memory definitions
PRU_ICSS     = 0x4A300000
PRU_ICSS_LEN = 512*1024
PRU_DRAM0    = 0x00000000
PRU_DRAM1    = 0x00002000
PRU_SRAM     = 0x00010000
MEMTYPES = [PRU_DRAM0, PRU_DRAM1, PRU_SRAM]

# Remoteproc functions
def modprobe():
    ret = subprocess.call("modprobe pru_rproc", shell=True)
    if ret > 0:
        print("modprobe failed")

def modunprobe():
    ret = subprocess.call("modprobe -r pru_rproc", shell=True)
    if ret > 0:
        print("modunprobe failed")

def pru_enable(number):
    try:
        if number == 0 or number == 1:
            with open('/sys/class/remoteproc/remoteproc'+str(number+1)+'/state', 'w') as fd:
                fd.write('start')
            fd.close()
            return 
        else:
            print("Number can be 0 or 1 only")
  
    except OSError:
         print("PRU already enabled!")
         return 

def pru_disable(number):
    try:
        with open('/sys/class/remoteproc/remoteproc'+str(number+1)+'/state', 'w') as fd:
            fd.write('stop')
        fd.close();
        return 
    except OSError:
        return 

def pru_reset(number):
    pru_disable(number)
    pru_enable(number)
    

def exec_program(filepath, number):
    pru_disable(number)
    if subprocess.call('cp '+filepath+' /lib/firmware/am335x-pru'+str(number)+'-fw', shell=True):
        print("Error loading firmware")
        return
    pru_enable(number)

# RPMsg functions
def send_msg(message, channel):
    devpath = '/dev/rpmsg_pru'+str(channel)
    if os.path.exists(devpath):
        with open(devpath, 'w') as fd:
            fd.write(message+'\n');
        fd.close()
    else:
        print("rpmsg channel not found!")

def get_msg(channel):
    devpath = '/dev/rpmsg_pru'+str(channel)
    if os.path.exists(devpath):
        with io.open(devpath, 'r') as fd:
            return fd.readline().strip()
        fd.close()
    else:
        print("rpmsg channel not found!")

def wait_for_event(eventno):
    if eventno == 0 or eventno == 1:
        devpath = '/dev/rpmsg_pru3'+str(eventno)
        if os.path.exists(devpath):
            with open(devpath, 'r') as fd:
                p = select.poll()
                p.register(fd)
                p.poll() 
            fd.close()
            return 1
        
        else:
            print("rpmsg channel not found")
    else:
        print("event can be 0 or 1 only")

#Memory functions
def writeint_prumem(memtype, address, data):
    if memtype < 0 or memtype > 2:
        print("Invalid memtype(Can be 0, 1, 2 only)")
        return
    with open('/dev/mem', 'r+b') as fd:
        pru_mem = mmap.mmap(fd.fileno(), PRU_ICSS_LEN, offset=PRU_ICSS)
        pru_mem[MEMTYPES[memtype]+address: MEMTYPES[memtype]+address+4] = struct.pack('L', data)
    pru_mem.close()
    fd.close()

def readint_prumem(memtype, address):
    if memtype < 0 or memtype > 2:
        print("Invalid memtype(Can be 0, 1, 2 only)")
        return
    with open('/dev/mem', 'r+b') as fd:
        pru_mem = mmap.mmap(fd.fileno(), PRU_ICSS_LEN, offset=PRU_ICSS)
        return struct.unpack('L', pru_mem[MEMTYPES[memtype]+address: MEMTYPES[memtype]+address+4])[0]
    pru_mem.close()
    fd.close()
    
def writebyte_prumem(memtype, address, data):
    if memtype < 0 or memtype > 2:
        print("Invalid memtype(Can be 0, 1, 2 only)")
        return
    with open('/dev/mem', 'r+b') as fd:
        pru_mem = mmap.mmap(fd.fileno(), PRU_ICSS_LEN, offset=PRU_ICSS)
        pru_mem[MEMTYPES[memtype]+address: MEMTYPES[memtype]+address+1] = struct.pack('B', data)
    pru_mem.close()
    fd.close()

def readbyte_prumem(memtype, address):
    if memtype < 0 or memtype > 2:
        print("Invalid memtype(Can be 0, 1, 2 only)")
        return
    with open('/dev/mem', 'r+b') as fd:
        pru_mem = mmap.mmap(fd.fileno(), PRU_ICSS_LEN, offset=PRU_ICSS)
        return struct.unpack('B', pru_mem[MEMTYPES[memtype]+address: MEMTYPES[memtype]+address+1])[0]
    pru_mem.close()
    fd.close()
                      

