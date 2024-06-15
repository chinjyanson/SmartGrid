from machine import Pin, I2C, ADC, PWM
from PID import PID
import network
import socket
import json
import _thread
import machine
import utime
from credentials import SSID, PASSWORD

# Function to connect to Wi-Fi
def connect_wifi(ssid, password):
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(ssid, password)
    print("Connecting to Wi-Fi...", end="")
    
    # Wait for the connection to complete
    while not wlan.isconnected():
        print(".", end="")
        utime.sleep(1)
    
    print(" Connected!")
    print("Network configuration:", wlan.ifconfig())

# Function to receive data from the server
def receive_from_server(client_socket):
    while True:
        try:
            data = client_socket.recv(1024)
            if not data:
                break
            received_json = data.decode('utf-8')
            parsed_data = json.loads(received_json)
            print(f"Received from server: {parsed_data}")
        except Exception as e:
            print(f"Error receiving data: {e}")
            break

# Function to send dummy data to the server
def send_to_server(client_socket, client_name, data):
    while True:
        # Generate dummy data with client name
        try:
            client_socket.sendall(json.dumps(data).encode('utf-8'))
            print(f"Sent to server: {data}")
        except Exception as e:
            print(f"Error sending data: {e}")
        
        utime.sleep(5)  # Wait 5 seconds before sending the next dummy data


# Function to start the client
def start_client(server_host, server_port, client_name, ssid, password, data):
    # Connect to Wi-Fi
    connect_wifi(ssid, password)
    
    # Create a socket and connect to the server
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((server_host, server_port))
    print(client_name.encode('utf-8'))
    client_socket.sendall(client_name.encode('utf-8'))  # Send the client's name to the server
    utime.sleep(3)

    # Start threads for sending and receiving data
    _thread.start_new_thread(receive_from_server, (client_socket,))
    send_to_server(client_socket, client_name, data)
    
server_host = '192.168.90.7'  # Replace with your server's IP address
server_port = 5555
client_name = 'solar'  # Replace with your client name
data = None

vret_pin = ADC(Pin(26))
vout_pin = ADC(Pin(28))
vin_pin = ADC(Pin(27))
pwm = PWM(Pin(0))
pwm.freq(100000)
pwm_en = Pin(1, Pin.OUT)

pid = PID(0.2, 10, 0, setpoint=0.3, scale='ms')

count = 0
pwm_out = 0
pwm_ref = 0
setpoint = 0.0
delta = 0.05
signal = 5

def saturate(duty):
    if duty > 62500:
        duty = 62500
    if duty < 100:
        duty = 100
    return duty

while True:
    
    pwm_en.value(1)

    vin = 1.026*(12490/2490)*3.3*(vin_pin.read_u16()/65536) # calibration factor * potential divider ratio * ref voltage * digital reading
    vout = 1.026*(12490/2490)*3.3*(vout_pin.read_u16()/65536) # calibration factor * potential divider ratio * ref voltage * digital reading
    vret = 1*3.3*((vret_pin.read_u16()-350)/65536) # calibration factor * potential divider ratio * ref voltage * digital reading
    count = count + 1
    
    
    pwm_ref = pid(vret)
    pwm_ref = int(pwm_ref*65536)
    pwm_out = saturate(pwm_ref)
    pwm.duty_u16(pwm_out)
    
    
    if count > 2000:
        print("Vin = {:.3f}".format(vin))
        print("Vout = {:.3f}".format(vout))
        print("Vret = {:.3f}".format(vret))
        print("Duty = {:.0f}".format(pwm_out))
        count = 0
        setpoint = setpoint + delta
                
        if setpoint > 0.4:
            setpoint = 0.4
            delta = - delta
        
        if setpoint < 0.05:
            setpoint = 0.05
            delta = -delta
            
        pid.setpoint = setpoint
    
    
    data = {"client": client_name,
            "timestamp": utime.time(),
            "value": pwm_out}
    start_client(server_host, server_port, client_name, SSID, PASSWORD, data)



