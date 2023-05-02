import _thread

import machine
import time

import uasyncio

crossing_request_button_a = machine.Pin(3, machine.Pin.IN, machine.Pin.PULL_DOWN)
crossing_request_button_b = machine.Pin(4, machine.Pin.IN, machine.Pin.PULL_DOWN)

car_semaphore_red_led = machine.Pin(2, machine.Pin.OUT)
car_semaphore_yellow_led = machine.Pin(1, machine.Pin.OUT)
car_semaphore_green_led = machine.Pin(0, machine.Pin.OUT)

pedestrian_waiting_control_led = machine.Pin(8, machine.Pin.OUT)
pedestrian_waiting_control_led.off()

pedestrian_semaphore_red_led = machine.Pin(6, machine.Pin.OUT)
pedestrian_semaphore_green_led = machine.Pin(7, machine.Pin.OUT)

buzzer = machine.PWM(machine.Pin(15))
buzzer.duty_u16(0)

pedestrian_crossing_lock = _thread.allocate_lock()

crossing_request = False
pedestrian_crossing = False

waiting_cycles_for_pedestrians = 0
cycles_count_after_crossing_request = 0


def set_car_semaphore(red: bool, yellow: bool, green: bool) -> None:
    car_semaphore_red_led.value(red)
    car_semaphore_yellow_led.value(yellow)
    car_semaphore_green_led.value(green)


def set_pedestrian_semaphore_free_walking(free_walking: bool) -> None:
    pedestrian_semaphore_red_led.value(not free_walking)
    pedestrian_semaphore_green_led.value(free_walking)


def pedestrian_baned_walking():
    global pedestrian_crossing_lock
    while True:
        print("banned walking")
        pedestrian_crossing_lock.acquire()

        print("banned walking - play")
        buzzer.duty_u16(32_767)
        time.sleep_ms(20)
        buzzer.duty_u16(0)
        time.sleep_ms(900)

        pedestrian_crossing_lock.release()
        print("banned walking - released")
        time.sleep_ms(20)


def pedestrian_free_walking():
    global crossing_request
    global pedestrian_crossing

    pedestrian_crossing = True
    pedestrian_crossing_lock.acquire()
    pedestrian_waiting_control_led.off()
    set_pedestrian_semaphore_free_walking(True)

    print("pedestrian started beeping")
    start_time = time.ticks_ms()
    while time.ticks_diff(time.ticks_ms(), start_time) < 5_000:
        buzzer.duty_u16(32_767)
        time.sleep_ms(20)
        buzzer.duty_u16(0)
        time.sleep_ms(125)
    print("pedestrian ended beeping")

    set_pedestrian_semaphore_free_walking(False)
    crossing_request = False
    pedestrian_crossing_lock.release()
    pedestrian_crossing = False


def crossing_button_handler(pin: machine.Pin):
    global crossing_request
    if not crossing_request:
        print("Crossing request button pressed > " + str(pin))
        crossing_request = True
        pedestrian_waiting_control_led.on()


crossing_request_button_a.irq(crossing_button_handler, machine.Pin.IRQ_RISING)
crossing_request_button_b.irq(crossing_button_handler, machine.Pin.IRQ_RISING)

set_car_semaphore(True, False, False)
set_pedestrian_semaphore_free_walking(False)

_thread.start_new_thread(pedestrian_baned_walking, ())

time.sleep(2)

while True:
    if crossing_request:
        cycles_count_after_crossing_request += 1

        if cycles_count_after_crossing_request >= 2 and waiting_cycles_for_pedestrians == 0:
            _thread.start_new_thread(pedestrian_free_walking, ())
            while crossing_request:
                time.sleep(1)
            waiting_cycles_for_pedestrians = 3
    set_car_semaphore(True, True, False)
    time.sleep(1)
    set_car_semaphore(False, False, True)
    time.sleep(3)
    set_car_semaphore(False, True, False)
    time.sleep(1)
    set_car_semaphore(True, False, False)
    if waiting_cycles_for_pedestrians > 0:
        waiting_cycles_for_pedestrians -= 1
