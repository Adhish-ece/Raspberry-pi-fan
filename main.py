  GNU nano 5.4                                                                                                    fan.py                                                                                                              
import RPi.GPIO as GPIO
import time

# Configuration
FAN_PIN = 17
PWM_FREQ = 10  # Hz (low frequency to simulate fan control)
MIN_TEMP = 40  # °C, start fan at low speed
MAX_TEMP = 65  # °C, full speed

# Setup
GPIO.setmode(GPIO.BCM)
GPIO.setup(FAN_PIN, GPIO.OUT)
fan_pwm = GPIO.PWM(FAN_PIN, PWM_FREQ)
fan_pwm.start(100)  # Start with fan OFF (100% high = logic 1 = OFF)

def get_cpu_temp():
    """Read CPU temperature in Celsius."""
    with open("/sys/class/thermal/thermal_zone0/temp", "r") as f:
        return int(f.read()) / 1000.0

def calc_duty_cycle(temp):
    """Map temperature to duty cycle (reverse logic)."""
    if temp < MIN_TEMP:
        return 100  # Fully off
    elif temp > MAX_TEMP:
        return 0    # Fully on
    else:
        # Linear interpolation (reverse logic)
        percent = (temp - MIN_TEMP) / (MAX_TEMP - MIN_TEMP)
        return 100 - (percent * 100)

try:
    while True:
        temp = get_cpu_temp()
        duty_cycle = calc_duty_cycle(temp)
        fan_pwm.ChangeDutyCycle(duty_cycle)
       # print(f"Temp: {temp:.1f}°C -> Fan Duty (reverse): {duty_cycle:.1f}%")
        time.sleep(5)

except KeyboardInterrupt:
   # print("Shutting down fan control.")
    fan_pwm.stop()
    GPIO.cleanup()


