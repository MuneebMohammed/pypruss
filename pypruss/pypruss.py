import os
import subprocess
import io
import select

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

def wait_for_event(number, channel):
    devpath = '/dev/rpmsg_pru'+str(channel)
    if os.path.exists(devpath):
        with open(devpath, 'r') as fd:
            p = select.poll()
            p.register(fd)
            p.poll() 
        fd.close()
        
    else:
        print("rpmsg channel not found")

