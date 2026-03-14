# Delcares the IRQ Pins for Reedswitches

import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)

BUTTON_GPIO_ReedA = 5
BUTTON_GPIO_ReedB = 6

GPIO.setup(BUTTON_GPIO_ReedA, GPIO.IN)
GPIO.setup(BUTTON_GPIO_ReedB, GPIO.IN)
GPIO.setup(BUTTON_GPIO_ReedA, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(BUTTON_GPIO_ReedB, GPIO.IN, pull_up_down=GPIO.PUD_UP)

while True:
	try:
		state_reetA = GPIO.input(BUTTON_GPIO_ReedA)
		print('state reet A: ', state_reetA)
		#button_callbackA(open_channel)

		state_reetB = GPIO.input(BUTTON_GPIO_ReedB)
		print('state reet B: ', state_reetB)
		#button_callbackB(open_channel)

	except KeyboardInterrupt or Exception or OSError as e:
		print("Termination", e)
		break
		GPIO.cleanup()
		sys.exit(1)
	time.sleep(0.02)
