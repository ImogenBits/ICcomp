import serial
import time

ser = serial.Serial(port = "COM3", baudrate = 115200, bytesize=8, timeout=2, stopbits=serial.STOPBITS_ONE)




time.sleep(2)
while ser.in_waiting:
	print(ser.read())

if True:
	ser.write(0xAA)