import pypruss

pypruss.modprobe()
pypruss.exec_program('./firmware_examples/blinky/gen/blinky.out', 1)
pypruss.pru_reset(1)
