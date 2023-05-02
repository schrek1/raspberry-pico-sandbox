import _thread

import machine
import time

button = machine.Pin(0, machine.Pin.IN, machine.Pin.PULL_DOWN)

led_red_1 = machine.Pin(1, machine.Pin.OUT)
led_red_2 = machine.Pin(2, machine.Pin.OUT)

leds = (led_red_1, led_red_2)
for led in leds: led.off()

buzzer = machine.PWM(machine.Pin(15))
buzzer.duty_u16(0)

frequency = 1_000
is_beeping = False


def perform_buzzer_beeping():
    global is_beeping
    on_time = 50
    print("beeping started")
    while is_beeping:
        buzzer.duty_u16(32_767)
        time.sleep_ms(on_time)
        buzzer.duty_u16(0)
        time.sleep_ms(1000 - on_time)
    print("beeping stoped")


def button_click_handler():
    global is_beeping
    is_beeping = not is_beeping
    if is_beeping:
        _thread.start_new_thread(perform_buzzer_beeping, ())


button.irq(button_click_handler, machine.Pin.IRQ_RISING)

while True:
    led_red_1.on()
    led_red_2.off()
    time.sleep_ms(1_000)
    led_red_1.off()
    led_red_2.on()
    time.sleep_ms(1_000)
