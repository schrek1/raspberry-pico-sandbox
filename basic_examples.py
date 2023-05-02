import machine
import utime as utime

led = machine.Pin(25, machine.Pin.OUT)
button = machine.Pin(0, machine.Pin.IN, machine.Pin.PULL_DOWN)

state = True

def led_blinking():
    led.on()
    print("led on for 2 seconds")
    utime.sleep(2)

    led.off()
    print("led off for 1 second")
    utime.sleep(1)


def led_controlled_by_button():
    led.value(button.value())


def led_with_state():
    global state
    if (button.value() == 1):
        if (state):
            state = False
        else:
            state = True
    led.value(state)


while True:
    led_with_state()
