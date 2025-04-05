import serial

def read_co2():
    ser = serial.Serial('/dev/ttyUSB0', 9600, timeout=1)
    ser.write(b'\xFE\x44\x00\x08\x02\x9F\x25')  # Command to read CO2
    response = ser.read(7)
    ser.close()

    if len(response) == 7:
        high, low = response[3], response[4]
        co2_ppm = (high << 8) | low
        return co2_ppm
    return None

if __name__ == "__main__":
    co2 = read_co2()
    print(f"CO2: {co2} ppm")
