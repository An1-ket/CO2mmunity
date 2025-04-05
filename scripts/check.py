import importlib

# List of required Python libraries
libraries = [
    "gpiozero",
    "lgpio",
    "serial",
    "adafruit_ssd1306",
    "PIL",
    "time",
    "threading",
    "spidev"  # Required for LoRa (SX1278)
]

print("Checking installed libraries...\n")

missing_libraries = []

for lib in libraries:
    try:
        importlib.import_module(lib)
        print(f"[✔] {lib} is installed.")
    except ImportError:
        print(f"[✘] {lib} is MISSING.")
        missing_libraries.append(lib)

# Additional System Checks
print("\nChecking system dependencies...\n")

# Check if the 1-Wire interface is enabled (for DS18B20 sensor)
try:
    with open("/sys/bus/w1/devices/w1_bus_master1/w1_master_slave_count", "r") as f:
        count = int(f.read().strip())
        if count > 0:
            print("[✔] DS18B20 sensor detected.")
        else:
            print("[✘] No DS18B20 sensor detected.")
except FileNotFoundError:
    print("[✘] 1-Wire interface may not be enabled. Run: sudo raspi-config -> Interface Options -> Enable 1-Wire.")

# Check if SPI is enabled (Required for LoRa SX1278)
try:
    with open("/boot/config.txt", "r") as f:
        config_lines = f.readlines()
        if any("dtparam=spi=on" in line for line in config_lines):
            print("[✔] SPI is enabled.")
        else:
            print("[✘] SPI is disabled. Run: sudo raspi-config -> Interface Options -> Enable SPI.")
except Exception as e:
    print(f"[!] Could not check SPI status: {e}")

# Summary
if missing_libraries:
    print("\nMissing libraries detected! Install them using:")
    print("sudo pip3 install " + " ".join(missing_libraries))
else:
    print("\nAll required libraries are installed!")

print("\nDependency check complete!")
