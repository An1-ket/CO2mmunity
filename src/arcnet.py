import time
import serial
import os
import threading
from gpiozero import OutputDevice
from oled.device import ssd1306
from oled.render import canvas
from PIL import ImageFont, ImageDraw

# -----------------------
# ✅ Initialize OLED Display
# -----------------------
device = ssd1306(port=1, address=0x3C)  # Ensure OLED address is 0x3C
font = ImageFont.load_default()

# -----------------------
# ✅ Initialize CO₂ Sensor (K33 ELG)
# -----------------------
try:
    co2_sensor = serial.Serial('/dev/ttyUSB0',9600, timeout=1)
    time.sleep(2)  # Allow sensor to stabilize
    print("✅ CO₂ Sensor Initialized!")
except Exception as e:
    print(f"❌ CO₂ Sensor Error: {e}")
    co2_sensor = None

# -----------------------
# ✅ Initialize DS18B20 Temperature Sensor
# -----------------------
temp_sensor_path = None
w1_device_folder = "/sys/bus/w1/devices/"
if os.path.exists(w1_device_folder):
    devices = os.listdir(w1_device_folder)
    for device in devices:
        if device.startswith("28-"):
            temp_sensor_path = f"{w1_device_folder}{device}/w1_slave"
            break

if temp_sensor_path:
    print(f"✅ DS18B20 Sensor Found: {temp_sensor_path}")
else:
    print("❌ DS18B20 Sensor Error: Not detected")

# -----------------------
# ✅ Initialize Relays
# -----------------------
relays = [OutputDevice(pin, active_high=False, initial_value=False) for pin in [5,6,13,19,26]]
print("✅ Relays Initialized! (All OFF at start)")

# -----------------------
# 🔍 Function to Read CO₂ Data
# -----------------------
def read_co2():
    if not co2_sensor:
        return "Error"
    
    try:
        co2_sensor.write(b"\xFE\x44\x00\x08\x02\x9F\x25")  # Command to read CO₂
        time.sleep(0.1)
        response = co2_sensor.read(7)
        if len(response) == 7:
            high_byte, low_byte = response[3], response[4]
            co2_value = (high_byte << 8) | low_byte
            return co2_value
        else:
            return "Error"
    except Exception as e:
        return f"Error: {e}"

# -----------------------
# 🌡️ Function to Read Temperature
# -----------------------
def read_temp():
    if not temp_sensor_path:
        return "Error"

    try:
        with open(temp_sensor_path, "r") as f:
            lines = f.readlines()
        
        if "YES" not in lines[0]:
            return "Error"

        temp_string = lines[1].split("t=")[-1]
        temp_c = float(temp_string) / 1000.0
        return round(temp_c, 2)
    except Exception as e:
        return "Error"

# -----------------------
# 📟 Function to Update OLED Display
# -----------------------
def update_oled():
    while True:
        co2 = read_co2()
        temp = read_temp()
        with canvas(device) as draw:
            draw.text((10, 5), f"CO2: {co2} ppm", font=font, fill=255)
            draw.text((10, 25), f"Temp: {temp} °C", font=font, fill=255)
        time.sleep(20)  # Update every 20 seconds

# -----------------------
# 🔌 Function to Control Relays via Keyboard
# -----------------------
def control_relays():
    print("🚀 Manual Relay Control Mode!")
    while True:
        try:
            cmd = input("\nEnter relay number (1-5) to toggle or 'q' to quit: ")
            if cmd.lower() == "q":
                print("Exiting relay control mode...")
                break
            elif cmd.isdigit() and 1 <= int(cmd) <= 5:
                relay_index = int(cmd) - 1
                relays[relay_index].toggle()
                print(f"🔄 Relay {cmd} toggled!")
            else:
                print("❌ Invalid input. Enter 1-5 or 'q' to quit.")
        except EOFError:
            print("❌ EOF Error: Running in background mode. Exiting input loop.")
            break

# -----------------------
# 🚀 Start OLED Thread (Runs in Background)
# -----------------------
if __name__ == "__main__":
    oled_thread = threading.Thread(target=update_oled, daemon=True)
    oled_thread.start()
    
    # If started manually, allow relay control
    control_relays()

