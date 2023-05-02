import machine
from machine import PWM, Pin

button_increase: Pin = machine.Pin(0, machine.Pin.IN, machine.Pin.PULL_DOWN)
button_decrease: Pin = machine.Pin(1, machine.Pin.IN, machine.Pin.PULL_DOWN)

buzzer: PWM = machine.PWM(machine.Pin(15))
buzzer.duty_u16(32_767)

frequency = 0


def button_irq_handler(pin: machine.Pin) -> None:
    global frequency
    step_size = 50
    if pin is button_increase:
        if frequency + step_size <= 2_000:
            frequency += step_size
            print("increased to " + str(frequency))
    if pin is button_decrease:
        if frequency - step_size >= 0:
            frequency -= step_size
            print("decreased to " + str(frequency))


button_increase.irq(button_irq_handler, machine.Pin.IRQ_RISING)
button_decrease.irq(button_irq_handler, machine.Pin.IRQ_RISING)

while True:
    print("actual frequency " + str(frequency))
    try:
        buzzer.freq(frequency)
    except ValueError:
        print("unable play frequency " + str(frequency))
