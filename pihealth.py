#!/usr/bin/env python3
from __future__ import division
from subprocess import PIPE, Popen
import sys
import psutil
import time
import board
import digitalio
import adafruit_character_lcd.character_lcd as characterlcd

# --------- User Settings ---------
# Set the number of minutes between checks
MINUTES_BETWEEN_READS = 1
# Set the number of seconds between Messages
SECONDS_BETWEEN_MSGS = 3
# Whether to output temp in C (True) or F (False)
METRIC_UNITS = False
# Whether to output CPU Usage per CPU Core
CPU_PERCENT_PER_CPU = True
# ---------------------------------

# Modify this if you have a different sized character LCD
lcd_columns = 16
lcd_rows = 2

# compatible with all versions of RPI as of Jan. 2019
# v1 - v3B+
lcd_rs = digitalio.DigitalInOut(board.D25)
lcd_en = digitalio.DigitalInOut(board.D24)
lcd_d4 = digitalio.DigitalInOut(board.D23)
lcd_d5 = digitalio.DigitalInOut(board.D17)
lcd_d6 = digitalio.DigitalInOut(board.D27)
lcd_d7 = digitalio.DigitalInOut(board.D22)


# Initialise the lcd class
lcd = characterlcd.Character_LCD_Mono(lcd_rs, lcd_en, lcd_d4, lcd_d5, lcd_d6,
                                      lcd_d7, lcd_columns, lcd_rows)

def get_cpu_temperature():
	process = Popen(['vcgencmd', 'measure_temp'], stdout=PIPE)
	output, _error = process.communicate()
	output = output.decode('utf-8')
	return float(output[output.index('=') + 1:output.rindex("'")])


def main():
	try:
		lcd.clear()
		while True:
			#BEGIN CPU TEMP
			cpu_temperature = get_cpu_temperature()
			msg = "CPU Temperature:\n"
			if METRIC_UNITS:
				msg = msg + str(cpu_temperature) + " (C)"
			else:
				cpu_temperature = cpu_temperature * 9.0 / 5.0 + 32.0
				msg = msg + str("{0:.2f}".format(cpu_temperature)) + " (F)"
			print(msg)
			lcd.message = msg
			#END CPU TEMP

			time.sleep(SECONDS_BETWEEN_MSGS)

			# BEGIN CPU USAGE
			lcd.clear()
			cpu_percent = psutil.cpu_percent(percpu=False)
			msg = "CPU Usage:\n" + str(cpu_percent) + " (%)"
			print(msg)
			lcd.message = msg
			#END CPU USAGE

			time.sleep(SECONDS_BETWEEN_MSGS)

			# BEGIN CPU USAGE (PER CPU)
			if CPU_PERCENT_PER_CPU:
				cpu_percents = psutil.cpu_percent(percpu=True)
				print ("Number of CPU Cores:", len(cpu_percents))
				if len(cpu_percents) > 0:
					for cpu in range(len(cpu_percents)):
						lcd.clear()
						msg = "CPU " + str(cpu+1) + " Usage:\n" + str(cpu_percents[cpu]) + " (%)"
						print(msg)
						lcd.message = msg
						time.sleep(SECONDS_BETWEEN_MSGS)
				else:
					print("INFO: No CPU Core Usage info available.")
					time.sleep(SECONDS_BETWEEN_MSGS)
			else:
				time.sleep(SECONDS_BETWEEN_MSGS)
			# END CPU USAGE (PER CPU)

			### BEGIN MEMORY STATS
			# BEGIN MEMORY TOTAL
			lcd.clear()
			mem = psutil.virtual_memory()
			mem_total = mem.total / 2**20
			msg = "Memory Total:\n" + str("{0:.2f}".format(mem_total)) + " (MB)"
			print(msg)
			lcd.message = msg
			# END MEMORY TOTAL

			time.sleep(SECONDS_BETWEEN_MSGS)

			# BEGIN MEMORY AVAILABLE
			lcd.clear()
			mem_avail = mem.available / 2**20
			msg = "Memory Avail:\n" + str("{0:.2f}".format(mem_avail)) + " (MB)"
			print(msg)
			lcd.message = msg
			# END MEMORY AVAILABLE

			time.sleep(SECONDS_BETWEEN_MSGS)

			# BEGIN MEMORY USED
			lcd.clear()
			mem_percent_used = mem.percent
			msg = "Memory Used:\n" + str("{0:.2f}".format(mem_percent_used)) + " (%)"
			print(msg)
			lcd.message =  msg
			# END MEMORY USED

			time.sleep(SECONDS_BETWEEN_MSGS)

			# BEGIN MEMORY FREE
			lcd.clear()
			mem_free = mem.free / 2**20
			msg = "Memory Free:\n" + str("{0:.2f}".format(mem_free)) + " (MB)"
			print(msg)
			lcd.message = msg
			# END MEMORY FREE
			### END MEMORY STATS

			time.sleep(SECONDS_BETWEEN_MSGS)
			lcd.clear()

			wait_time = 60*MINUTES_BETWEEN_READS

			while wait_time:
				mins, secs = divmod(wait_time, 60)
				timeformat = '{:02d}:{:02d}'.format(mins, secs)
				msg = "Next status in: " + timeformat
				print(msg, end='\r')
				lcd.message = msg
				time.sleep(1)
				wait_time -= 1

	except KeyboardInterrupt:
        	print("Keyboard Interrupt detected. Exiting...")
        	lcd.clear()
        	sys.exit(0)
	except:
        	print("Following error occurred: ", sys.exc_info())
        	lcd.clear()
        	sys.exit(1)

if __name__ == '__main__':
	main()
