import os
import subprocess

def modprobe():
    ret = subprocess.call("modprobe pru_rproc", shell=True)
    print(ret);



