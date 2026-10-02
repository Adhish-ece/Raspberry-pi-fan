# 🌡️ Raspberry Pi PWM Fan Controller

An automated, dynamic, and lightweight Python script designed to manage Raspberry Pi cooling fan speeds using **Pulse Width Modulation (PWM)** based on real-time CPU thermal statistics.

---

## 📌 Features

- **Dynamic Temperature Scaling:** Automatically scales fan duty cycle linearly between **40°C** and **65°C**.
- **Active-Low / Inverted Logic:** Engineered for PNP transistor or N-Channel MOSFET driver circuits where Logic HIGH = Fan OFF and Logic LOW = Fan FULL SPEED.
- **Minimal CPU Footprint:** Executes periodic checks every 5 seconds to conserve Pi resources.
- **Auto-Start on Boot:** Pre-configured with `crontab` execution so your Pi is immediately cooled when powered on.

---

## 🛠 Hardware Setup & Pinout

Below is the standard wiring table for connecting your fan switch circuit to the Raspberry Pi GPIO headers:

| Component | Function | Raspberry Pi Header Pin | BCM Pin |
| :--- | :--- | :--- | :--- |
| **Transistor Gate / Base** | PWM Control Signal | Pin 11 | GPIO 17 |
| **Ground (GND)** | Common Ground | Pin 6 or Pin 9 | Ground |
| **5V / 3.3V Power** | Fan Supply Positive | Pin 2 / Pin 4 (5V) | VCC |

---

## 📐 Circuit Logic & Equations

This script employs inverted PWM duty cycle logic to suit active-low hardware driver configurations:

$$\text{Duty Cycle (\%)} = 100 - \left( \frac{\text{Temp} - \mathrm{MIN_TEMP}}{\mathrm{MAX_TEMP} - \mathrm{MIN_TEMP}} \times 100 \right)$$

- **Temp $< 40^\circ\text{C}$**: Duty Cycle = `100%` (Logic HIGH $\rightarrow$ Fan **OFF**)
- **Temp $> 65^\circ\text{C}$**: Duty Cycle = `0%` (Logic LOW $\rightarrow$ Fan **FULL SPEED**)
- **$40^\circ\text{C} \le \text{Temp} \le 65^\circ\text{C}$**: Smooth linear transition between off and 100% speed.

---

## 🚀 Requirements & Installation

### 1. System Package Manager (Recommended)
Install `RPi.GPIO` via `apt` on Raspberry Pi OS:

```bash
sudo apt update
sudo apt install -y python3-rpi.gpio
```

### 2. Python PIP Package Manager
If using a virtual environment (`venv`), create a `requirements.txt` file containing:

```text
RPi.GPIO
```

And install with pip:
```bash
pip install -r requirements.txt
```

---

## 🐍 Python Controller Script (`fan_control.py`)

Save the following Python code as `fan_control.py`:

```python
import RPi.GPIO as GPIO
import time

# Configuration
FAN_PIN = 17   # BCM GPIO pin
PWM_FREQ = 10  # Hz (low frequency for software PWM control)
MIN_TEMP = 40  # °C, start fan at low speed
MAX_TEMP = 65  # °C, full speed

# Setup
GPIO.setmode(GPIO.BCM)
GPIO.setup(FAN_PIN, GPIO.OUT)
fan_pwm = GPIO.PWM(FAN_PIN, PWM_FREQ)
fan_pwm.start(100)  # Start with fan OFF (100% duty cycle = logic 1 = OFF)

def get_cpu_temp():
    """Read CPU temperature in Celsius."""
    with open("/sys/class/thermal/thermal_zone0/temp", "r") as f:
        return int(f.read()) / 1000.0

def calc_duty_cycle(temp):
    """Map temperature to duty cycle (reverse active-low logic)."""
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
        time.sleep(5)

except KeyboardInterrupt:
    fan_pwm.stop()
    GPIO.cleanup()
```

---

## ⏰ Auto-Start on Boot (Crontab Setup)

To start the fan controller automatically whenever your Raspberry Pi boots:

1. Open the crontab editor:
   ```bash
   crontab -e
   ```

2. Add the following line at the end of the file:
   ```text
   @reboot /usr/bin/python3 /home/pi/fan_control.py &
   ```
   *(Make sure to update `/home/pi/fan_control.py` to your actual script path. The `&` ensures background execution).*

3. Save and exit (Press `Ctrl + O`, `Enter`, then `Ctrl + X` in `nano`).

4. Reboot to verify:
   ```bash
   sudo reboot
   ```

---

## 📄 License
This project is open-source and released under the [MIT License](LICENSE).
