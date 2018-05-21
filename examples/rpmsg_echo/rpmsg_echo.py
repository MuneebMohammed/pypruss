import pypruss

pypruss.modprobe()
pypruss.exec_program('./rpmsg_echo.out', 0)
pypruss.send_msg('Hello PRU0', 30)
print(pypruss.get_msg(30))
