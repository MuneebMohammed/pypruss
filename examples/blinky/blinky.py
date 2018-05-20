import pypruss

pypruss.modprobe()
pypruss.exec_program('./blinky.out', 1)
pypruss.pru_reset(1)
