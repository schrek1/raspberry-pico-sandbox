import machine
import utime
import _thread

led_red = machine.Pin(15, machine.Pin.OUT)
led_red.off()
led_yellow = machine.Pin(14, machine.Pin.OUT)
led_yellow.off()
led_green = machine.Pin(13, machine.Pin.OUT)
led_green.off()

button = machine.Pin(16, machine.Pin.IN, machine.Pin.PULL_DOWN)
buzzer = machine.Pin(12, machine.Pin.OUT)
buzzer.off()
build_led = machine.Pin(25, machine.Pin.OUT)
build_led.off()

global button_pressed
button_pressed = False


def button_reader_thread():
    global button_pressed
    while True:
        if button.value() == 1:
            print("button pressed")
            button_pressed = True


_thread.start_new_thread(button_reader_thread, ())

while True:
    if button_pressed:
        print("walking button action")
        led_red.on()
        for i in range(10):
            buzzer.on()
            utime.sleep(0.2)
            buzzer.off()
            utime.sleep(0.2)
        global button_pressed
        button_pressed = False

    print("red - stop")
    led_red.on()
    utime.sleep(5)

    print("yellow - prepare for green")
    led_yellow.on()
    utime.sleep(2)

    print("green - go")
    led_red.off()
    led_yellow.off()
    led_green.on()
    utime.sleep(10)

    print("yellow - prepare for red")
    led_green.off()
    led_yellow.on()
    utime.sleep(3)
    led_yellow.off()
