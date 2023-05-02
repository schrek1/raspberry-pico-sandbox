import _thread

import machine
import time

crossing_request_button_a = machine.Pin(3, machine.Pin.IN, machine.Pin.PULL_DOWN)
crossing_request_button_b = machine.Pin(4, machine.Pin.IN, machine.Pin.PULL_DOWN)

car_semaphore_red_led = machine.Pin(2, machine.Pin.OUT)
car_semaphore_yellow_led = machine.Pin(1, machine.Pin.OUT)
car_semaphore_green_led = machine.Pin(0, machine.Pin.OUT)

pedestrian_waiting_control_led = machine.Pin(1, machine.Pin.OUT)
pedestrian_semaphore_red_led = machine.Pin(2, machine.Pin.OUT)
pedestrian_semaphore_green_led = machine.Pin(0, machine.Pin.OUT)

buzzer = machine.PWM(machine.Pin(15))
buzzer.duty_u16(0)
buzzer_current_frequency = 1_000

crossing_request = False
cycles_count_after_last_crossing = 0


def set_car_semaphore(red: bool, yellow: bool, green: bool) -> None:
    car_semaphore_red_led.value(red)
    car_semaphore_yellow_led.value(yellow)
    car_semaphore_green_led.value(green)


def set_pedestrian_semaphore_free_walking(free_walking: bool) -> None:
    pedestrian_semaphore_red_led.value(not free_walking)
    pedestrian_semaphore_green_led.value(free_walking)


def pedestrian_free_walking():
    global crossing_request
    set_pedestrian_semaphore_free_walking(True)
    pedestrian_waiting_control_led.off()
    print("pedestrian started beeping")
    for _ in range(10):
        buzzer.duty_u16(32_767)
        time.sleep_ms(50)
        buzzer.duty_u16(0)
        time.sleep_ms(950)
    print("pedestrian ended beeping")
    set_pedestrian_semaphore_free_walking(False)
    crossing_request = False


def crossing_button_handler(pin: machine.Pin):
    global crossing_request
    if crossing_request == False:
        print("Crossing request button pressed > " + str(pin))
        crossing_request = True
        pedestrian_waiting_control_led.on()


crossing_request_button_a.irq(crossing_request_button_a, machine.Pin.IRQ_RISING)
crossing_request_button_b.irq(crossing_request_button_a, machine.Pin.IRQ_RISING)

set_car_semaphore(True, False, False)
set_pedestrian_semaphore_free_walking(False)

time.sleep(2)

while True:
    global cycles_count_after_last_crossing
    print("cycles_count_after_last_crossing = " + str(cycles_count_after_last_crossing))
    if crossing_request and cycles_count_after_last_crossing > 3:
        _thread.start_new_thread(pedestrian_free_walking, ())
        while crossing_request:
            time.sleep(1)
        cycles_count_after_last_crossing = 0
    else:
        set_car_semaphore(True, True, False)
        time.sleep(1)
        set_car_semaphore(False, False, True)
        time.sleep(3)
        set_car_semaphore(False, True, False)
        time.sleep(1)
        set_car_semaphore(3)
        cycles_count_after_last_crossing += 1
