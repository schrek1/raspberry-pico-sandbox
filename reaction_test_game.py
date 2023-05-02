import machine
import time
import utime
import random

signal_led = machine.Pin(15, machine.Pin.OUT)

green_led = machine.Pin(13, machine.Pin.OUT)
yellow_led = machine.Pin(12, machine.Pin.OUT)

leds = [signal_led, green_led, yellow_led]

green_button = machine.Pin(16, machine.Pin.IN, machine.Pin.PULL_DOWN)
yellow_button = machine.Pin(14, machine.Pin.IN, machine.Pin.PULL_DOWN)


global fastest_button
fastest_button = None

def button_handler(pin):
    print("button pressed - " + str(pin))
    green_button.irq(None)
    yellow_button.irq(None)
    reaction_time = time.ticks_diff(time.ticks_ms(), timer_start)
    winner_player = ""
    if pin == green_button:
        winner_player = "green"
        green_led.on()
    elif pin == yellow_button:
        winner_player = "yellow"
        yellow_led.on()
    print("Player " + winner_player + " is winner!!!")
    print("Your reaction time was " + str(reaction_time) + " ms!")


print("start")
for led in leds:
    led.off()
utime.sleep(random.uniform(5, 10))
print("led is on")
signal_led.on()
timer_start = time.ticks_ms()
green_button.irq(button_handler, machine.Pin.IRQ_RISING)
yellow_button.irq(button_handler, machine.Pin.IRQ_RISING)
