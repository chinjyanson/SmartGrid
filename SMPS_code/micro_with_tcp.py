from machine import Pin, I2C, ADC, PWM, Timer
from tcp_client import Tcp_client, connect_to_wifi
import time
import ujson

# Set up some pin allocations for the Analogues and switches
va_pin = ADC(Pin(28))
vb_pin = ADC(Pin(26))
vpot_pin = ADC(Pin(27))
OL_CL_pin = Pin(12, Pin.IN, Pin.PULL_UP)
BU_BO_pin = Pin(2, Pin.IN, Pin.PULL_UP)

# Set up the I2C for the INA219 chip for current sensing
ina_i2c = I2C(0, scl=Pin(1), sda=Pin(0), freq=100000)  # Reduced frequency for stability

# Some PWM settings, pin number, frequency, duty cycle limits and start with the PWM outputting the default of the min value.
pwm = PWM(Pin(9))
pwm.freq(100000)
min_pwm = 1000
max_pwm = 64536
pwm_out = min_pwm
pwm_ref = 30000

# Some error signals
trip = 0
OC = 0

# The potentiometer is prone to noise so we are filtering the value using a moving average
v_pot_filt = [0] * 100
v_pot_index = 0

# Gains etc for the PID controller
i_ref = 0 # Voltage reference for the CL modes
i_err = 0 # Voltage error
i_err_int = 0 # Voltage error integral
i_pi_out = 0 # Output of the voltage PI controller
kp = 100 # Boost Proportional Gain
ki = 300 # Boost Integral Gain

# Basic signals to control logic flow
global timer_elapsed
timer_elapsed = 0
count = 0
first_run = 1
hold_vpot = 1

# Need to know the shunt resistance
global SHUNT_OHMS
SHUNT_OHMS = 0.10

# Saturation function for anything you want saturated within bounds
def saturate(signal, upper, lower):
    return max(min(signal, upper), lower)

# This is the function executed by the loop timer, it simply sets a flag which is used to control the main loop
def tick(t):
    global timer_elapsed
    timer_elapsed = 1

# These functions relate to the configuring of and reading data from the INA219 Current sensor
class ina219:
    # Register Locations
    REG_CONFIG = 0x00
    REG_SHUNTVOLTAGE = 0x01
    REG_BUSVOLTAGE = 0x02
    REG_POWER = 0x03
    REG_CURRENT = 0x04
    REG_CALIBRATION = 0x05
    
    def __init__(self, sr, address):
        self.address = address
        self.shunt = sr
            
    def vshunt(self):
        try:
            reg_bytes = ina_i2c.readfrom_mem(self.address, self.REG_SHUNTVOLTAGE, 2)
            reg_value = int.from_bytes(reg_bytes, 'big')
            if reg_value > 2**15:  # Negative
                reg_value -= 2**16
            return float(reg_value) * 1e-5
        except Exception as e:
            print(f"INA219 vshunt error: {e}")
            return 0
        
    def vbus(self):
        try:
            reg_bytes = ina_i2c.readfrom_mem(self.address, self.REG_BUSVOLTAGE, 2)
            reg_value = int.from_bytes(reg_bytes, 'big') >> 3
            return float(reg_value) * 0.004
        except Exception as e:
            print(f"INA219 vbus error: {e}")
            return 0
        
    def configure(self):
        try:
            ina_i2c.writeto_mem(self.address, self.REG_CONFIG, b'\x19\x9F')  # PG = /8
            ina_i2c.writeto_mem(self.address, self.REG_CALIBRATION, b'\x00\x00')
        except Exception as e:
            print(f"INA219 configure error: {e}")

name = "cell"
client = None

def connect_to_server():
    global client
    try:
        if client:
            client.close()
        client = Tcp_client(host='192.168.90.7', port=9998, client_name=name, blocking=True)
        client.connect()
        print("TCP connected")
        return True
    except Exception as e:
        print(f"Error connecting to server: {e}")
        return False

def reconnect_client():
    global client
    print("Attempting to reconnect...")
    if client:
        client.close()
    return connect_to_server()

try:
    connect_to_wifi()
    print("WiFi connected")

    # Attempt to connect to the server with retries
    max_retries = 5
    for attempt in range(max_retries):
        if connect_to_server():
            break
        else:
            print(f"Retrying to connect to server (attempt {attempt + 1}/{max_retries})...")
            time.sleep(5)  # Delay before retrying

    if not client or not client.is_connected:
        raise Exception("Failed to connect to server after multiple attempts")
    
    time.sleep(2)  # Allow some time for server stabilization
except Exception as e:
    print(f"TCP client setup error: {e}")

data = {
    'name': name,
    'value': 1234,
    'timestamp': time.time()
}

try:
    while True:
        if first_run:
            # for first run, set up the INA link and the loop timer settings
            ina = ina219(SHUNT_OHMS, 0x40)  # Replace 0x40 with the detected I2C address
            ina.configure()
            first_run = 0
            
            # This starts a 1kHz timer which we use to control the execution of the control loops and sampling
            loop_timer = Timer(mode=Timer.PERIODIC, freq=1000, callback=tick)
        
        if timer_elapsed == 1:
            va = 1.017 * (12490 / 2490) * 3.3 * (va_pin.read_u16() / 65536)
            vb = 1.015 * (12490 / 2490) * 3.3 * (vb_pin.read_u16() / 65536)
            
            if 1 <= hold_vpot <= 7500:
                vpot = 1.19
                hold_vpot += 1
            elif hold_vpot > 7500:
                vpot = 1.19
                hold_vpot = 0
            else:
                vpot_in = 1.026 * 3.3 * (vpot_pin.read_u16() / 65536)
                v_pot_filt[v_pot_index] = vpot_in
                v_pot_index = (v_pot_index + 1) % 100
                vpot = sum(v_pot_filt) / 100
                vpot = saturate(vpot, 1.35, 0.75)
            
            Vshunt = ina.vshunt()
            CL = OL_CL_pin.value()
            BU = BU_BO_pin.value()
                
            min_pwm = 0 
            max_pwm = 64536
            iL = Vshunt / SHUNT_OHMS
            pwm_ref = saturate(65536 - int((vpot / 3.3) * 65536), max_pwm, min_pwm)
                  
            if CL != 1:
                i_err_int = 0
                
                if iL > 2:
                    pwm_out = pwm_out - 10
                    OC = 1
                    pwm_out = saturate(pwm_out, pwm_ref, min_pwm)
                elif iL < -2:
                    pwm_out = pwm_out + 10
                    OC = 1
                    pwm_out = saturate(pwm_out, max_pwm, pwm_ref)
                else:
                    pwm_out = pwm_ref
                    OC = 0
                    pwm_out = saturate(pwm_out, pwm_ref, min_pwm)
                    
                duty = 65536 - pwm_out
                pwm.duty_u16(duty)
                
            else:
                i_ref = saturate(vpot - 1.66, 1.5, -1.5)
                i_err = i_ref - iL
                i_err_int = i_err_int + i_err
                i_err_int = saturate(i_err_int, 10000, -10000)
                i_pi_out = (kp * i_err) + (ki * i_err_int)
                
                pwm_out = saturate(i_pi_out, max_pwm, min_pwm)
                duty = int(65536 - pwm_out)
                pwm.duty_u16(duty)
            
            data['value'] = pwm_out
            data['timestamp'] = time.time()
            
            retry_count = 0
            max_retries = 5
            
            while retry_count < max_retries:
                try:
                    if client and client.is_connected:
                        client.send_data(data)
                        response = client.receive_data()
                        print(f"Received response: {response}")
                    else:
                        print("Not connected to server, attempting to reconnect...")
                        if reconnect_client():
                            print("Reconnected successfully")
                        else:
                            print("Reconnection failed")
                    break
                except OSError as e:
                    print(f"OSError during send/receive: {e}")
                    time.sleep(1)
                    retry_count += 1
                except Exception as e:
                    print(f"General error during send/receive: {e}")
                    reconnect_client()
                    break
            
            timer_elapsed = 0
            count += 1
            if count > 100:
                print(f"Va = {va:.3f}")
                print(f"Vb = {vb:.3f}")
                print(f"Vpot = {vpot:.3f}")
                print(f"iL = {iL:.3f}")
                print(f"OC = {OC}")
                print(f"CL = {CL}")
                print(f"BU = {BU}")
                print(f"Duty = {duty}")
                print(f"Hold_vpot = {hold_vpot}")
                print(f"i_err = {i_err:.3f}")
                print(f"i_ref = {i_ref:.3f}")
                count = 0

            time.sleep(5)  # Wait for 5 seconds before the next iteration

except Exception as e:
    print(f"Main loop error: {e}")

finally:
    if client:
        client.close()

