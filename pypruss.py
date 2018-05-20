import os
import subprocess

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
            with open('/sys/class/remoteproc/remoteproc'+str(number+1)+'/state', 'w+') as fd:
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
        with open('/sys/class/remoteproc/remoteproc'+str(number+1)+'/state', 'w+') as fd:
            fd.write('stop')
        fd.close();
        return 
    except OSError:
        return 

def pru_reset(number):
    pru_disable(number)
    pru_enable(number)
    

def exec_program(filepath, number):
    with open(filepath, 'r') as f:
        with open('/lib/firmware/am335x-pru'+str(number)+'-fw', 'w') as f1:
            for line in f:
                f1.write(line);
    f.close();
    f1.close();
    pru_reset(number);

