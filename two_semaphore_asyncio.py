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

device_led = machine.Pin(25, machine.Pin.OUT)

buzzer = machine.PWM(machine.Pin(15))
buzzer.duty_u16(0)

crossing_request_event = uasyncio.Event()
pedestrian_crossing_free_event = uasyncio.Event()


def set_car_semaphore(red: bool, yellow: bool, green: bool) -> None:
    car_semaphore_red_led.value(red)
    car_semaphore_yellow_led.value(yellow)
    car_semaphore_green_led.value(green)


def set_pedestrian_semaphore_free_walking(free_walking: bool) -> None:
    pedestrian_semaphore_red_led.value(not free_walking)
    pedestrian_semaphore_green_led.value(free_walking)


async def pedestrian_buzzer_control():
    while True:
        if not pedestrian_crossing_free_event.is_set():
            buzzer.duty_u16(32_767)
            await uasyncio.sleep_ms(20)
            buzzer.duty_u16(0)
            await uasyncio.sleep_ms(900)
        await uasyncio.sleep(0)


async def pedestrian_semaphore_control():
    crossing_request_event.clear()
    pedestrian_crossing_free_event.set()

    set_pedestrian_semaphore_free_walking(True)

    start_time = time.ticks_ms()
    while time.ticks_diff(time.ticks_ms(), start_time) < 5_000:
        buzzer.duty_u16(32_767)
        await uasyncio.sleep_ms(20)
        buzzer.duty_u16(0)
        await uasyncio.sleep_ms(125)

    set_pedestrian_semaphore_free_walking(False)
    pedestrian_crossing_free_event.clear()


async def pedestrian_walking_control_led_blink():
    while True:
        if crossing_request_event.is_set():
            pedestrian_waiting_control_led.on()
            await uasyncio.sleep_ms(500)
            pedestrian_waiting_control_led.off()
            await uasyncio.sleep_ms(500)
        await uasyncio.sleep(0)


async def device_control_led_blink():
    while True:
        for _ in range(2):
            device_led.on()
            await uasyncio.sleep_ms(300)
            device_led.off()
            await uasyncio.sleep_ms(200)
        await uasyncio.sleep(2)


async def crossing_button_handler():
    while True:
        if crossing_request_button_a.value():
            print("Crossing request button a pressed")
            crossing_request_event.set()
            while crossing_request_button_a.value():
                await uasyncio.sleep(0)
        if crossing_request_button_b.value():
            print("Crossing request button b pressed")
            crossing_request_event.set()
            while crossing_request_button_b.value():
                await uasyncio.sleep(0)
        await uasyncio.sleep_ms(0)


async def main():
    car_semaphore_cycles_count_after_request_pedestrian_crossing = 0
    car_semaphore_cycles_waiting_for_pedestrians = 0

    set_car_semaphore(True, False, False)
    set_pedestrian_semaphore_free_walking(False)

    await uasyncio.sleep(2)

    uasyncio.create_task(device_control_led_blink())
    uasyncio.create_task(crossing_button_handler())
    uasyncio.create_task(pedestrian_buzzer_control())
    uasyncio.create_task(pedestrian_walking_control_led_blink())

    while True:
        if crossing_request_event.is_set():
            car_semaphore_cycles_count_after_request_pedestrian_crossing += 1

            if car_semaphore_cycles_count_after_request_pedestrian_crossing >= 2 \
                    and car_semaphore_cycles_waiting_for_pedestrians == 0:
                await pedestrian_semaphore_control()
                car_semaphore_cycles_waiting_for_pedestrians = 3
                car_semaphore_cycles_count_after_request_pedestrian_crossing = 0

        set_car_semaphore(True, True, False)
        await uasyncio.sleep(1)

        set_car_semaphore(False, False, True)
        await uasyncio.sleep(3)

        set_car_semaphore(False, True, False)
        await uasyncio.sleep(1)

        set_car_semaphore(True, False, False)
        await uasyncio.sleep(3)

        if car_semaphore_cycles_waiting_for_pedestrians > 0:
            car_semaphore_cycles_waiting_for_pedestrians -= 1


try:
    uasyncio.run(main())
finally:
    uasyncio.new_event_loop()
