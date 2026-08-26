# Delcares the IRQ Pins for Reedswitches

import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)

GPIO.setup(16, GPIO.OUT)

BUTTON_GPIO = 16

try:
	state_reetA = GPIO.output(BUTTON_GPIO, GPIO.HIGH)
	print('state reet A: ', state_reetA)

	time.sleep(3)

	#state_reetB = GPIO.output(BUTTON_GPIO, GPIO.LOW)
	#print('state reet B: ', state_reetB)

	GPIO.cleanup()

except KeyboardInterrupt or Exception or OSError as e:
	print("Termination", e)
	GPIO.cleanup()
	sys.exit(1)
	time.sleep(0.02)
