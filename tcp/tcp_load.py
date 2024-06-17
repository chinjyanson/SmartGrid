from machine import Pin, I2C, ADC, PWM
from PID import PID
import network
import socket
import ujson
import _thread
import random
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

def receive_from_server(client_socket, client_name):
    while True:
        try:
            data = client_socket.recv(1024)
            if data:                
                # Decode and parse the received JSON data
                received_json = data.decode('utf-8')
                print(received_json)
                parsed_data = json.loads(received_json)
                
                # Check if 'toClient' matches client_name
                if isinstance(parsed_data, list):
                    for message in parsed_data:
                        print("Message: ",message)
                        if message.get("client") == client_name:
                            print(f"Received from server: {message}")
                        else:
                            print(f"Ignored message for {message.get('client')}")
                else:
                    if parsed_data.get("client") == client_name:
                        print(f"Received from server: {parsed_data}")
                    else:
                        print(f"Ignored message for {parsed_data.get('client')}")
        except Exception as e:
            print(f"Error receiving data: {e}")
            break

# Function to send dummy data to the server
def send_to_server(client_socket, data):
    while True:
        # Generate dummy data with client name
        try:
            client_socket.sendall(ujson.dumps(data).encode('utf-8'))
            print(f"Sent to server: {data}")
        except Exception as e:
            print(f"Error sending data: {e}")
        
        utime.sleep(5)  # Wait 5 seconds before sending the next dummy data


# Function to start the client
def start_client(server_host, server_port, client_name, ssid, password):
    # Connect to Wi-Fi
    connect_wifi(ssid, password)
    
    # Create a socket and connect to the server
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((server_host, server_port))
    print(client_name.encode('utf-8'))
    client_socket.sendall(client_name.encode('utf-8'))  # Send the client's name to the server
    utime.sleep(3)

    # Start threads for sending and receiving data
    _thread.start_new_thread(receive_from_server, (client_socket,client_name, ))
    
    return client_socket
    
server_host = '192.168.90.163'  # Replace with your server's IP address
server_port = 5555
client_name = 'load'  # Replace with your client name
client_socket = start_client(server_host, server_port, client_name, SSID, PASSWORD)
data = None

vret_pin = ADC(Pin(26))
vout_pin = ADC(Pin(28))
vin_pin = ADC(Pin(27))
pwm = PWM(Pin(0))
pwm.freq(100000)
pwm_en = Pin(1, Pin.OUT)
vret_sum = 0
total_vret_readings = 0
tolerance = 5

pid = PID(0.2, 10, 0, setpoint=0.3, scale='ms')

count = 0
pwm_out = 0
pwm_ref = 0
setpoint = 0.0
delta = 0.01
max_sp = 0.07

def saturate(duty):
    if duty > 62500:
        duty = 62500
    if duty < 100:
        duty = 100
    return duty

def power_Calc(vout, vret):
    return vout*vret/1.02

while True:
    pwm_en.value(1)
    required_power = random.randint(1,15)/10
    stop = False
    
    while not stop:
        vin = 1.026*(12490/2490)*3.3*(vin_pin.read_u16()/65536) # calibration factor * potential divider ratio * ref voltage * digital reading
        vout = 1.026*(12490/2490)*3.3*(vout_pin.read_u16()/65536) # calibration factor * potential divider ratio * ref voltage * digital reading
        vret = 1*3.3*((vret_pin.read_u16()-350)/65536) # calibration factor * potential divider ratio * ref voltage * digital reading
        count = count + 1      
        pwm_ref = pid(vret)
        pwm_ref = int(pwm_ref*65536)
        pwm.duty_u16(pwm_out)
        vret_sum+=vret
        total_vret_readings+=1
        average_vret = vret_sum/total_vret_readings

        current_Power = power_Calc(vout, vret)
        print("Current Power:",current_Power)
        print("Required Power:",required_power)
        if current_Power< required_power*(1-tolerance/100):
            pwm_out+=100
        elif current_Power > required_power*(1+tolerance/100):
            pwm_out-=100
        elif required_power*(1-tolerance/100) <= current_Power <= required_power*(1+tolerance/100):
            print("Power Achieved")
            stop = True
        print(pwm_out)
    


    utime.sleep(1)

    print("Vin = {:.3f}".format(vin))
    print("Vout = {:.3f}".format(vout))
    print("Vret = {:.3f}".format(vret))
    print("Average Vret = {:.3f}".format(average_vret))
    print("Duty = {:.0f}".format(pwm_out))
    
    if count > 2000:
        
        count = 0
        setpoint = setpoint + delta
                
        if setpoint > max_sp:
            setpoint = max_sp
            delta = - delta
        
        if setpoint <= 0:
            setpoint = 0
            delta = -delta
            
        pid.setpoint = setpoint
        
    data = {"client": client_name,
        "timestamp": utime.time(),
        "value": pwm_out}
    send_to_server(client_socket, data)




